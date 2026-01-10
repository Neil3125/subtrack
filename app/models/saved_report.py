"""Saved Report model for storing user report configurations."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SavedReport(Base):
    """Model for saving report configurations."""
    
    __tablename__ = "saved_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # 'subscriptions', 'analytics', 'outstanding', etc.
    configuration = Column(JSON, nullable=False)  # Store all report parameters as JSON
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<SavedReport(id={self.id}, name='{self.name}', type='{self.report_type}')>"
