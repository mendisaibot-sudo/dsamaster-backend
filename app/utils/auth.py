"""JWT authentication utilities."""

import os
import time
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

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
    """Verify the request has a valid admin JWT."""
    user = await get_current_user(request)
    if user.get("sub") != BLOG_ADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
