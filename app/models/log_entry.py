"""Log entry model for log check functionality."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class LogEntry(Base):
    """Log entry model for storing generated log checks."""
    
    __tablename__ = "log_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Log details
    date_str = Column(String(20), nullable=False)  # e.g., "1/23/2026"
    start_time = Column(String(20), nullable=False)  # e.g., "2:30 p.m"
    end_time = Column(String(20), nullable=False)  # e.g., "3:00 p.m"
    duration_minutes = Column(Integer, nullable=False)
    
    # Check type: 'service', 'backup', 'custom', 'onsite'
    check_type = Column(String(20), nullable=False, index=True)
    category_name = Column(String(100), nullable=True)  # For custom checks
    message = Column(Text, nullable=False)
    
    # Full formatted log entry
    full_entry = Column(Text, nullable=False)
    
    # Optional customer association
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    customer = relationship("Customer", backref="log_entries")
    
    def __repr__(self):
        return f"<LogEntry(id={self.id}, check_type='{self.check_type}', date='{self.date_str}')>"
