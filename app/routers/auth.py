"""Authentication router."""

from fastapi import APIRouter, HTTPException, Request

from app.models.blog import AuthResponse
from app.utils.auth import (
    verify_credentials,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(request: Request):
    """Authenticate with username/password and return a JWT token."""
    import json
    body = await request.body()
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return AuthResponse(success=False, error="Invalid JSON body")

    username = data.get("username", "")
    password = data.get("password", "")

    if not verify_credentials(username, password):
        return AuthResponse(success=False, error="Invalid username or password")

    token = create_access_token(username, expires_hours=24)
    return AuthResponse(
        success=True,
        data={
            "token": token,
            "user": {
                "username": username
            }
        }
    )


@router.post("/logout", response_model=AuthResponse)
async def logout():
    """Logout - mainly handled client-side by removing the token."""
    return AuthResponse(success=True, data={"message": "Logged out successfully"})


@router.get("/me", response_model=AuthResponse)
async def get_me(request: Request):
    """Get current authenticated user info."""
    try:
        current_user = await get_current_user(request)
        return AuthResponse(
            success=True,
            data={
                "user": {
                    "username": current_user["sub"]
                }
            }
        )
    except HTTPException as e:
        return AuthResponse(success=False, error=e.detail)


@router.get("/verify", response_model=AuthResponse)
async def verify(request: Request):
    """Verify if the current token is valid."""
    try:
        current_user = await get_current_user(request)
        return AuthResponse(success=True, data={"valid": True, "user": {"username": current_user["sub"]}})
    except HTTPException as e:
        return AuthResponse(success=False, error=e.detail)
