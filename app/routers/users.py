"""User management API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.routers.auth_routes import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_model=List[UserResponse])
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users (admin only)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).order_by(User.id).all()
    return users


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user (admin only)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if username exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists (if provided)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        is_admin=user_data.is_admin,
        is_active=True
    )
    user.set_password(user_data.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user (admin only)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a user (admin only)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if new username is taken
    if user_data.username and user_data.username != user.username:
        existing = db.query(User).filter(User.username == user_data.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = user_data.username
    
    # Check if new email is taken
    if user_data.email is not None:
        if user_data.email and user_data.email != user.email:
            existing = db.query(User).filter(User.email == user_data.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_data.email
    
    if user_data.password:
        user.set_password(user_data.password)
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    if user_data.is_admin is not None:
        user.is_admin = user_data.is_admin
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user (admin only)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting the admin user
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete the admin user")
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}
