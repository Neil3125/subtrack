"""Check category model for log check custom categories."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.database import Base


class CheckCategory(Base):
    """Category model for custom log check types."""
    
    __tablename__ = "check_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)  # Default message for this category
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CheckCategory(id={self.id}, name='{self.name}')>"
