"""Link schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.link import EntityType, UserDecision


class LinkResponse(BaseModel):
    """Schema for link response."""
    id: int
    source_type: EntityType
    source_id: int
    target_type: EntityType
    target_id: int
    confidence: float = Field(..., ge=0, le=1)
    evidence_text: str
    created_at: datetime
    user_decision: Optional[UserDecision]
    
    class Config:
        from_attributes = True


class LinkDecision(BaseModel):
    """Schema for user decision on a link."""
    decision: UserDecision
