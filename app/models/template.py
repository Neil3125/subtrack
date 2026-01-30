"""Subscription template model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.subscription import BillingCycle

class SubscriptionTemplate(Base):
    __tablename__ = "subscription_templates"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(200), index=True, nullable=False)
    plan_name = Column(String(200), nullable=True) # e.g. "Premium", "Family"
    cost = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    billing_cycle = Column(Enum(BillingCycle), nullable=False)
    
    # Optional category pre-selection
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="templates")
