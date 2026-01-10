"""Group schemas."""
from pydantic import BaseModel, Field
from typing import Optional


class GroupBase(BaseModel):
    """Base group schema."""
    name: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


class GroupCreate(GroupBase):
    """Schema for creating a group."""
    category_id: int


class GroupUpdate(BaseModel):
    """Schema for updating a group."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    notes: Optional[str] = None
    category_id: Optional[int] = None


class GroupResponse(GroupBase):
    """Schema for group response."""
    id: int
    category_id: int
    
    class Config:
        from_attributes = True
