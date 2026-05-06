"""Admin panel endpoints for user management."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models.user import User, UserStats, UserProgress
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


class AdminUserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool


@router.get("/users")
async def get_users(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all users (admin only)."""
    current_user = get_current_user(request, db)
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).all()
    return {
        "success": True,
        "users": [u.to_dict() for u in users]
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a user (admin only)."""
    current_user = get_current_user(request, db)
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from uuid import UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "email" in data:
        # Check if email is already taken by another user
        existing = db.query(User).filter(User.email == data["email"], User.id != user_uuid).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = data["email"]
    if "role" in data:
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = data["is_active"]
    if "is_verified" in data:
        user.email_verified = data["is_verified"]
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "user": user.to_dict()
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)."""
    current_user = get_current_user(request, db)
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from uuid import UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {
        "success": True,
        "message": "User deleted successfully"
    }


@router.get("/stats")
async def get_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get admin dashboard stats (admin only)."""
    current_user = get_current_user(request, db)
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.email_verified == True).count()
    
    # Count total problems solved across all users
    total_problems_solved = db.query(func.sum(UserStats.total_solved)).scalar() or 0
    
    return {
        "success": True,
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "total_problems_solved": int(total_problems_solved)
        }
    }
