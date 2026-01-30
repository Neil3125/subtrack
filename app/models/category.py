"""Category model."""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

# Import association table for subscription many-to-many
from app.models.associations import subscription_categories
from app.database import Base


class Category(Base):
    """Category model for organizing subscriptions."""
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    groups = relationship("Group", back_populates="category", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="category", viewonly=True)
    subscriptions = relationship("Subscription", back_populates="category", cascade="all, delete-orphan")
    templates = relationship("SubscriptionTemplate", back_populates="category")

    # Many-to-many subscriptions
    subscriptions_many = relationship(
        "Subscription",
        secondary=subscription_categories,
        back_populates="categories",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
