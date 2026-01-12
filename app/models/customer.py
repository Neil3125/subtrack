"""Customer model."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.associations import customer_categories, customer_groups


class Customer(Base):
    """Customer model for tracking subscription owners.
    
    Now supports many-to-many relationships with categories and groups.
    The old category_id and group_id are kept for backward compatibility during migration.
    """
    
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    # Legacy fields - kept for backward compatibility
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=False, index=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags
    notes = Column(Text, nullable=True)
    
    # Many-to-many relationships
    categories = relationship(
        "Category",
        secondary=customer_categories,
        back_populates="related_customers",
        lazy="selectin"
    )
    groups = relationship(
        "Group",
        secondary=customer_groups,
        back_populates="related_customers",
        lazy="selectin"
    )
    
    # Legacy relationships - kept for backward compatibility
    primary_category = relationship("Category", foreign_keys=[category_id], viewonly=True)
    primary_group = relationship("Group", foreign_keys=[group_id], viewonly=True)
    
    # Subscriptions relationship
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}')>"
    
    @property
    def category_names(self):
        """Get comma-separated list of category names."""
        return ", ".join([cat.name for cat in self.categories]) if self.categories else ""
    
    @property
    def group_names(self):
        """Get comma-separated list of group names."""
        return ", ".join([grp.name for grp in self.groups]) if self.groups else ""
