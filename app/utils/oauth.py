"""OAuth configuration and utilities for Google and GitHub login."""

import os
import secrets

import bcrypt
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserStats
from app.utils.auth import create_access_token
from app.db import get_db
from datetime import datetime

# OAuth credentials from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "https://dsamaster.de")

REDIRECT_URI = f"{FRONTEND_BASE_URL}/api/auth/oauth/{{provider}}/callback"

# Initialize OAuth registry
oauth = OAuth()

# Register Google provider
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

# Register GitHub provider
if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    oauth.register(
        name="github",
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        api_base_url="https://api.github.com",
        client_kwargs={"scope": "read:user user:email"},
        # GitHub doesn't follow OAuth2 strictly for token response, tolerate text
        token_endpoint_auth_method="client_secret_post",
    )


def _generate_random_password() -> str:
    """Generate a secure random password for OAuth users."""
    return secrets.token_urlsafe(48)


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _create_refresh_token(user_id: str, db: Session) -> str:
    """Create a refresh token for a user (import here to avoid circular import)."""
    import hashlib
    from datetime import timedelta, timezone
    from app.models.user import AuthToken

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
    auth_token = AuthToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(auth_token)
    db.commit()
    return raw_token


def find_or_create_oauth_user(
    provider: str,
    oauth_id: str,
    email: str,
    name: str,
    avatar: str | None,
    db: Session
) -> tuple[str, str]:
    """
    Find an existing user by OAuth provider+id or email, or create a new one.
    Returns (access_token, refresh_token).
    """
    # 1. Try to find by oauth_id + provider
    user = db.query(User).filter(
        User.oauth_provider == provider,
        User.oauth_id == oauth_id,
    ).first()

    # 2. If not found, try by email
    if not user:
        user = db.query(User).filter(User.email == email).first()

    if user:
        # Update OAuth fields if user exists but didn't have OAuth linked
        if not user.oauth_provider:
            user.oauth_provider = provider
            user.oauth_id = oauth_id
        if not user.avatar_url and avatar:
            user.avatar_url = avatar
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    else:
        # 3. Create new user
        # Parse name into first/last
        name_parts = name.strip().split(" ", 1)
        first_name = name_parts[0] or "User"
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        display_name = name.strip() or first_name

        raw_password = _generate_random_password()
        password_hash = _hash_password(raw_password)

        new_user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            oauth_provider=provider,
            oauth_id=oauth_id,
            avatar_url=avatar,
            is_active=True,
            email_verified=True,
            captcha_verified=True,
        )
        db.add(new_user)
        db.flush()

        # Create user stats record
        stats = UserStats(user_id=new_user.id)
        db.add(stats)

        db.commit()
        db.refresh(new_user)
        user = new_user

    # Create tokens (same format as existing login flow)
    access_token = create_access_token(str(user.id), expires_hours=24)
    refresh_token = _create_refresh_token(str(user.id), db)

    return access_token, refresh_token
