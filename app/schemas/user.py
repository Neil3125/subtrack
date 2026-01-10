"""User schemas for API validation."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    email: str


class ResetPasswordRequest(BaseModel):
    """Schema for reset password request."""
    token: str
    new_password: str
