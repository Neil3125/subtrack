"""Customer schemas."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class CategoryInfo(BaseModel):
    """Minimal category info for response."""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class GroupInfo(BaseModel):
    """Minimal group info for response."""
    id: int
    name: str
    category_id: int
    
    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    """Base customer schema."""
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    country: str = Field(..., min_length=1, max_length=100)  # Now required
    tags: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating a customer.
    
    Supports both single (legacy) and multiple categories/groups.
    """
    # Legacy single relationship fields (for backward compatibility)
    category_id: Optional[int] = None
    group_id: Optional[int] = None
    
    # New many-to-many relationship fields
    category_ids: Optional[List[int]] = None
    group_ids: Optional[List[int]] = None


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[str] = None
    notes: Optional[str] = None
    
    # Legacy single relationship fields
    category_id: Optional[int] = None
    group_id: Optional[int] = None
    
    # New many-to-many relationship fields
    category_ids: Optional[List[int]] = None
    group_ids: Optional[List[int]] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: int
    
    # Legacy fields for backward compatibility
    category_id: Optional[int] = None
    group_id: Optional[int] = None
    
    # Many-to-many relationships
    categories: List[CategoryInfo] = []
    groups: List[GroupInfo] = []
    
    # Helper properties
    category_names: str = ""
    group_names: str = ""
    
    class Config:
        from_attributes = True
