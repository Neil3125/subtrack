"""Renewal notice tracking model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class RenewalNotice(Base):
    """Model for tracking sent renewal email notifications.
    
    This prevents duplicate emails by recording when notices are sent.
    """
    
    __tablename__ = "renewal_notices"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Email details
    recipient_email = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    
    # Status tracking
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Notice type (e.g., "7_day", "14_day", "30_day")
    notice_type = Column(String(50), nullable=False, default="manual")
    
    # Renewal date at time of sending (for reference)
    renewal_date_at_send = Column(DateTime, nullable=True)
    
    # Relationships
    subscription = relationship("Subscription", backref="renewal_notices")
    customer = relationship("Customer", backref="renewal_notices")
    
    def __repr__(self):
        return f"<RenewalNotice(id={self.id}, subscription_id={self.subscription_id}, sent_at={self.sent_at}, success={self.success})>"
