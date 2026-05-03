"""User authentication and registration endpoints."""

import base64
import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User, AuthToken, UserStats, UserProgress, Submission
from app.utils.auth import create_access_token, verify_token
from app.utils.captcha import create_captcha, verify_captcha

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    display_name: str | None = None
    captcha_id: str
    captcha_answer: str

    @validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('first_name', 'last_name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def _create_refresh_token(user_id: str, db: Session) -> str:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(days=7)
    auth_token = AuthToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(auth_token)
    db.commit()
    return raw_token

def _revoke_refresh_token(token: str, db: Session):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    auth_token = db.query(AuthToken).filter(
        AuthToken.token_hash == token_hash,
        AuthToken.revoked_at.is_(None)
    ).first()
    if auth_token:
        auth_token.revoked_at = datetime.utcnow()
        db.commit()
        return True
    return False

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    
    payload = verify_token(auth_header[7:])
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/captcha")
async def generate_captcha():
    captcha = create_captcha()
    image_b64 = base64.b64encode(captcha["image"]).decode()
    return {
        "success": True,
        "data": {
            "captcha_id": captcha["captcha_id"],
            "image": f"data:image/png;base64,{image_b64}",
            "expires_at": captcha["expires_at"]
        }
    }

@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if not verify_captcha(data.captcha_id, data.captcha_answer):
        raise HTTPException(status_code=400, detail="Invalid or expired CAPTCHA")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    display_name = data.display_name or f"{data.first_name} {data.last_name}"
    user = User(
        email=data.email,
        password_hash=_hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        display_name=display_name,
        captcha_verified=True,
        is_active=True,
        role="user"
    )
    db.add(user)
    db.flush()

    stats = UserStats(user_id=user.id)
    db.add(stats)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(str(user.id), expires_hours=24)
    refresh_token = _create_refresh_token(str(user.id), db)

    return {
        "success": True,
        "token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }

@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.is_active == True).first()
    if not user or not _verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token(str(user.id), expires_hours=24)
    refresh_token = _create_refresh_token(str(user.id), db)

    return {
        "success": True,
        "token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }

@router.post("/refresh")
async def refresh(data: dict, db: Session = Depends(get_db)):
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token required")

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    auth_token = db.query(AuthToken).filter(
        AuthToken.token_hash == token_hash,
        AuthToken.revoked_at.is_(None),
        AuthToken.expires_at > datetime.utcnow()
    ).first()

    if not auth_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == auth_token.user_id).first()
    access_token = create_access_token(str(user.id), expires_hours=24)
    new_refresh_token = _create_refresh_token(str(user.id), db)
    _revoke_refresh_token(refresh_token, db)

    return {
        "success": True,
        "token": access_token,
        "refresh_token": new_refresh_token,
        "user": user.to_dict()
    }

@router.post("/logout")
async def logout(data: dict, db: Session = Depends(get_db)):
    refresh_token = data.get("refresh_token")
    if refresh_token:
        _revoke_refresh_token(refresh_token, db)
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"success": True, "user": current_user.to_dict()}
