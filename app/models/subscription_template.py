"""Subscription Template model."""
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.subscription import BillingCycle

class SubscriptionTemplate(Base):
    """Template for quickly creating subscriptions."""
    
    __tablename__ = "subscription_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True) # User-friendly name e.g. "Work Adobe"
    
    # Template fields (optional defaults)
    vendor_name = Column(String(200), nullable=True)
    plan_name = Column(String(200), nullable=True)
    cost = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True, default="USD")
    billing_cycle = Column(Enum(BillingCycle), nullable=True)
    
    # Organization
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    category = relationship("Category")
    
    def __repr__(self):
        return f"<SubscriptionTemplate(id={self.id}, name='{self.name}')>"
