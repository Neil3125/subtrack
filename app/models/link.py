"""Link model for AI-discovered relationships."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class EntityType(str, enum.Enum):
    """Entity type enum."""
    CATEGORY = "category"
    GROUP = "group"
    CUSTOMER = "customer"
    SUBSCRIPTION = "subscription"


class UserDecision(str, enum.Enum):
    """User decision on link suggestion."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Link(Base):
    """Link model for tracking relationships between entities."""
    
    __tablename__ = "links"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(Enum(EntityType), nullable=False, index=True)
    source_id = Column(Integer, nullable=False, index=True)
    target_type = Column(Enum(EntityType), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    evidence_text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
    user_decision = Column(Enum(UserDecision), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Link(id={self.id}, {self.source_type}:{self.source_id} -> {self.target_type}:{self.target_id}, confidence={self.confidence})>"
