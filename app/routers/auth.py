"""User authentication and registration endpoints."""

import base64
import hashlib
import re
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
from app.utils.email import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

SPECIAL_CHARS = set("!@#$%^&*()-_=+[]{}|;:'\",.<>?/~`")


def _validate_password_strength(password: str):
    """Validate password strength and return list of missing requirements."""
    errors = []
    if len(password) < 12:
        errors.append("at least 12 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("at least 1 uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("at least 1 lowercase letter")
    if not re.search(r"\d", password):
        errors.append("at least 1 digit")
    if not any(c in SPECIAL_CHARS for c in password):
        errors.append("at least 1 special character (!@#$%^&* etc.)")
    return errors


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    display_name: str | None = None
    captcha_id: str
    captcha_answer: str

    @validator("password")
    def password_strength(cls, v):
        missing = _validate_password_strength(v)
        if missing:
            raise ValueError(
                "Password must contain: " + ", ".join(missing)
            )
        return v

    @validator("first_name", "last_name")
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @validator("new_password")
    def password_strength(cls, v):
        missing = _validate_password_strength(v)
        if missing:
            raise ValueError(
                "Password must contain: " + ", ".join(missing)
            )
        return v


class ResendVerificationRequest(BaseModel):
    email: EmailStr


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
    verification_token = secrets.token_urlsafe(32)
    verification_expires = datetime.utcnow() + timedelta(hours=48)

    user = User(
        email=data.email,
        password_hash=_hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        display_name=display_name,
        captcha_verified=True,
        is_active=False,
        role="user",
        verification_token=verification_token,
        verification_token_expires_at=verification_expires
    )
    db.add(user)
    db.flush()

    stats = UserStats(user_id=user.id)
    db.add(stats)
    db.commit()
    db.refresh(user)

    # Send verification email
    try:
        send_verification_email(user.email, verification_token)
    except Exception:
        # Don't fail registration if email fails, but log it
        pass

    return {
        "success": True,
        "message": "Registration successful. Please check your email to verify your account."
    }


@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    if user.verification_token_expires_at and datetime.utcnow() > user.verification_token_expires_at:
        raise HTTPException(status_code=400, detail="Verification token has expired")

    user.email_verified = True
    user.is_active = True
    user.verification_token = None
    user.verification_token_expires_at = None
    db.commit()

    return {
        "success": True,
        "message": "Account registration completed successfully and email verified"
    }


@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend the verification email for a pending account."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or user.email_verified:
        # Return success to avoid email enumeration
        return {
            "success": True,
            "message": "If an unverified account exists, a verification email has been sent."
        }

    # Generate new token
    verification_token = secrets.token_urlsafe(32)
    verification_expires = datetime.utcnow() + timedelta(hours=48)
    user.verification_token = verification_token
    user.verification_token_expires_at = verification_expires
    db.commit()

    try:
        send_verification_email(user.email, verification_token)
    except Exception:
        pass

    return {
        "success": True,
        "message": "If an unverified account exists, a verification email has been sent."
    }


@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not _verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in"
        )

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is deactivated")

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


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.utcnow() + timedelta(hours=24)
        user.reset_token = reset_token
        user.reset_token_expires_at = reset_expires
        db.commit()

        try:
            send_password_reset_email(user.email, reset_token)
        except Exception:
            pass

    # Always return success to prevent email enumeration
    return {
        "success": True,
        "message": "If an account exists with this email, a password reset link has been sent."
    }


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == data.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if user.reset_token_expires_at and datetime.utcnow() > user.reset_token_expires_at:
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user.password_hash = _hash_password(data.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()

    return {
        "success": True,
        "message": "Password has been reset successfully."
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