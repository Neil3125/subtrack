"""Subscription model."""
from sqlalchemy import Column, Integer, String, Text, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import date
import enum
from app.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    EXPIRED = "expired"


class BillingCycle(str, enum.Enum):
    """Billing cycle enum."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    BIANNUAL = "biannual"


class Subscription(Base):
    """Subscription model for tracking recurring services."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    vendor_name = Column(String(200), nullable=False, index=True)
    plan_name = Column(String(200), nullable=True)
    cost = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    billing_cycle = Column(Enum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    start_date = Column(Date, nullable=False, default=date.today)
    next_renewal_date = Column(Date, nullable=False, index=True)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")
    category = relationship("Category", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, vendor='{self.vendor_name}', customer_id={self.customer_id})>"
    
    def days_until_renewal(self) -> int:
        """Calculate days until next renewal."""
        if not self.next_renewal_date:
            return 999999
        delta = self.next_renewal_date - date.today()
        return delta.days
    
    def is_expiring_soon(self, threshold_days: int = 30) -> bool:
        """Check if subscription is expiring soon."""
        return 0 <= self.days_until_renewal() <= threshold_days
    
    def is_overdue(self) -> bool:
        """Check if subscription is overdue."""
        return self.days_until_renewal() < 0
