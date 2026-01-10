"""AI Request Cache model for storing cached AI responses."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime, timedelta
from app.database import Base
from app.config import settings


class AIRequestCache(Base):
    """Cache for AI API requests to save daily API quota."""
    
    __tablename__ = "ai_request_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    request_hash = Column(String(64), unique=True, nullable=False, index=True)
    request_type = Column(String(50), nullable=False, index=True)  # link_intelligence, budget_surgeon, etc.
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    hit_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Create composite index for efficient cache lookups
    __table_args__ = (
        Index('idx_cache_hash_expires', 'request_hash', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<AIRequestCache(id={self.id}, type='{self.request_type}', hash='{self.request_hash[:8]}...')>"
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create_expiry(cls) -> datetime:
        """Create an expiry timestamp based on configured TTL."""
        return datetime.utcnow() + timedelta(seconds=settings.ai_cache_ttl)
