"""Category model."""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.associations import customer_categories


class Category(Base):
    """Category model for organizing subscriptions.
    
    Now supports many-to-many relationship with customers.
    """
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    groups = relationship("Group", back_populates="category", cascade="all, delete-orphan")
    
    # Many-to-many relationship with customers
    related_customers = relationship(
        "Customer",
        secondary=customer_categories,
        back_populates="categories",
        lazy="selectin"
    )
    
    subscriptions = relationship("Subscription", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
