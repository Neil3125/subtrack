"""Customer model."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Try to import association tables - they may not exist if migration hasn't run
try:
    from app.models.associations import customer_categories, customer_groups
    ASSOCIATIONS_AVAILABLE = True
except Exception:
    customer_categories = None
    customer_groups = None
    ASSOCIATIONS_AVAILABLE = False


class Customer(Base):
    """Customer model for tracking subscription owners.
    
    Supports many-to-many relationships with categories and groups when available.
    Falls back to legacy single category_id/group_id if migration hasn't been run.
    """
    
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    # Legacy fields - used as primary relationship fields
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True, index=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags
    notes = Column(Text, nullable=True)
    
    # Legacy relationships - always available
    category = relationship("Category", foreign_keys=[category_id], viewonly=True)
    group = relationship("Group", foreign_keys=[group_id], viewonly=True)
    
    # Subscriptions relationship
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}')>"
    
    @property
    def categories(self):
        """Get list of categories - returns list with single category for compatibility."""
        if self.category:
            return [self.category]
        return []
    
    @property
    def groups(self):
        """Get list of groups - returns list with single group for compatibility."""
        if self.group:
            return [self.group]
        return []
    
    @property
    def primary_category(self):
        """Alias for category for backward compatibility."""
        return self.category
    
    @property
    def primary_group(self):
        """Alias for group for backward compatibility."""
        return self.group
    
    @property
    def category_names(self):
        """Get comma-separated list of category names."""
        if self.category:
            return self.category.name
        return ""
    
    @property
    def group_names(self):
        """Get comma-separated list of group names."""
        if self.group:
            return self.group.name
        return ""
