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


class CustomerResponse(BaseModel):
    """Schema for customer response."""
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    
    # Legacy fields for backward compatibility
    category_id: Optional[int] = None
    group_id: Optional[int] = None
    
    # Many-to-many relationships
    categories: List[CategoryInfo] = []
    groups: List[GroupInfo] = []
    
    # List of group IDs for easier frontend handling
    group_ids: List[int] = []
    
    # Computed fields for display
    category_names: Optional[str] = ""
    group_names: Optional[str] = ""
    
    class Config:
        from_attributes = True
    
    def __init__(self, **data):
        # Handle SQLAlchemy model conversion
        if 'categories' in data and data['categories']:
            # Check if it's a list of ORM objects
            cats = data['categories']
            if cats and hasattr(cats[0], 'id'):
                data['categories'] = [{'id': c.id, 'name': c.name} for c in cats]
                data['category_names'] = ', '.join([c.name for c in cats])
        
        if 'groups' in data and data['groups']:
            # Check if it's a list of ORM objects
            grps = data['groups']
            if grps and hasattr(grps[0], 'id'):
                data['groups'] = [{'id': g.id, 'name': g.name, 'category_id': g.category_id} for g in grps]
                data['group_names'] = ', '.join([g.name for g in grps])
                # Also populate group_ids for easier frontend handling
                data['group_ids'] = [g.id for g in grps]
        
        # Ensure group_ids is populated from groups if not already set
        if 'group_ids' not in data or not data['group_ids']:
            if 'groups' in data and data['groups']:
                data['group_ids'] = [g['id'] if isinstance(g, dict) else g.id for g in data['groups']]
        
        super().__init__(**data)
