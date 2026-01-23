"""Check category model for log check custom categories."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class CheckCategory(Base):
    """Category model for custom log check types."""
    
    __tablename__ = "check_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # Removed unique constraint for multi-user support logic
    description = Column(Text, nullable=True)  # Default message for this category
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CheckCategory(id={self.id}, name='{self.name}')>"
