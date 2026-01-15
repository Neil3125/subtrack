"""Customer model."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Import association tables for many-to-many relationships
from app.models.associations import customer_categories, customer_groups


class Customer(Base):
    """Customer model for tracking subscription owners.
    
    Supports many-to-many relationships with groups via the customer_groups association table.
    The category_id field is the primary category assignment.
    """
    
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    # Primary category field
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    # Legacy single group field - kept for backward compatibility
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True, index=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags
    notes = Column(Text, nullable=True)
    
    # Primary category relationship (legacy / backward compatible)
    category = relationship("Category", foreign_keys=[category_id], viewonly=True)
    
    # Many-to-many categories relationship (new)
    _categories = relationship(
        "Category",
        secondary=customer_categories,
        lazy="selectin"
    )
    
    # Legacy single group relationship (for backward compatibility)
    _legacy_group = relationship("Group", foreign_keys=[group_id], viewonly=True)
    
    # Many-to-many relationship with groups
    _groups = relationship(
        "Group",
        secondary=customer_groups,
        backref="customers_multi",
        lazy="selectin"
    )
    
    # Subscriptions relationship
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}')>"
    
    @property
    def categories(self):
        """Get list of all categories (many-to-many).
        
        Falls back to primary category if no many-to-many categories set.
        """
        if self._categories and len(self._categories) > 0:
            return list(self._categories)
        elif self.category:
            return [self.category]
        return []
    
    @property
    def groups(self):
        """Get list of all groups the customer belongs to (many-to-many).
        
        Falls back to legacy single group if no many-to-many groups are set.
        """
        if self._groups and len(self._groups) > 0:
            return list(self._groups)
        elif self._legacy_group:
            return [self._legacy_group]
        return []
    
    @property
    def primary_category(self):
        """Alias for category for backward compatibility."""
        return self.category
    
    @property
    def primary_group(self):
        """Get the primary (first) group for backward compatibility."""
        if self._groups and len(self._groups) > 0:
            return self._groups[0]
        return self._legacy_group
    
    @property
    def category_names(self):
        """Get comma-separated list of category names."""
        cats = self.categories
        if cats:
            return ", ".join([c.name for c in cats])
        return ""
    
    def set_categories(self, categories_list):
        """Set the many-to-many categories relationship.
        
        Args:
            categories_list: List of Category objects to assign to this customer
        """
        self._categories = categories_list
        # Also update primary category_id for backward compatibility
        if categories_list and len(categories_list) > 0:
            self.category_id = categories_list[0].id
        else:
            self.category_id = None
    
    @property
    def group_names(self):
        """Get comma-separated list of group names."""
        groups = self.groups
        if groups:
            return ", ".join([g.name for g in groups])
        return ""
    
    def set_groups(self, groups_list):
        """Set the many-to-many groups relationship.
        
        Args:
            groups_list: List of Group objects to assign to this customer
        """
        self._groups = groups_list
        # Also update legacy group_id for backward compatibility
        if groups_list and len(groups_list) > 0:
            self.group_id = groups_list[0].id
        else:
            self.group_id = None
