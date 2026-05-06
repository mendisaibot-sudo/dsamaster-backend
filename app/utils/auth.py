"""JWT authentication utilities for blog API."""

import os
import time
import uuid
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.db import SessionLocal
from app.models.user import User

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-not-for-production")
BLOG_ADMIN_USERNAME = os.getenv("BLOG_ADMIN_USERNAME", "admin")
BLOG_ADMIN_PASSWORD = os.getenv("BLOG_ADMIN_PASSWORD", "admin123")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BlogHTTPBearer(HTTPBearer):
    """Custom bearer that returns None for missing credentials (to allow public routes)."""
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        try:
            return await super().__call__(request)
        except HTTPException:
            return None


security_bearer = BlogHTTPBearer(auto_error=False)


def create_access_token(username: str, expires_hours: int = 24) -> str:
    """Create a JWT access token."""
    expire = time.time() + (expires_hours * 3600)
    payload = {
        "sub": username,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_credentials(username: str, password: str) -> bool:
    """Verify username/password against configured credentials."""
    # For simplicity with env-set passwords: compare plaintext.
    # In a hashed setup you would use pwd_context.verify(password, hash).
    return username == BLOG_ADMIN_USERNAME and password == BLOG_ADMIN_PASSWORD


async def get_current_user_optional(request: Request) -> Optional[dict]:
    """Extract current user from Authorization header if present; return None otherwise."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    try:
        return verify_token(auth_header[7:])
    except HTTPException:
        return None


async def get_current_user(request: Request) -> dict:
    """Require and return the current user from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    return verify_token(auth_header[7:])


async def require_admin(request: Request) -> dict:
    """Verify the request has a valid admin JWT (role-based check)."""
    token_payload = await get_current_user(request)
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing sub claim")
    
    try:
        uuid_user_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == uuid_user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return {"sub": user_id, "role": user.role, "email": user.email}
    finally:
        db.close()


async def require_admin_fallback(request: Request) -> dict:
    """Legacy fallback: verify token sub matches BLOG_ADMIN_USERNAME."""
    token_payload = await get_current_user(request)
    if token_payload.get("sub") != BLOG_ADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Admin access required")
    return token_payload
