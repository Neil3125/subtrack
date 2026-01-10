"""Category schemas."""
from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int
    
    class Config:
        from_attributes = True
