"""Customer schemas."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class CustomerBase(BaseModel):
    """Base customer schema."""
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a customer."""
    category_id: int
    group_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    category_id: Optional[int] = None
    group_id: Optional[int] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: int
    category_id: int
    group_id: Optional[int]
    country: Optional[str] = None
    
    class Config:
        from_attributes = True
