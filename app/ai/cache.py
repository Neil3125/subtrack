"""AI request caching system to save API quota."""
import hashlib
import json
import functools
import logging
from typing import Optional, Callable, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.ai_cache import AIRequestCache
from app.config import settings

logger = logging.getLogger(__name__)


def generate_cache_key(request_type: str, **params) -> str:
    """
    Generate a unique hash key for a cache request.
    
    Args:
        request_type: Type of AI request (e.g., 'link_intelligence', 'budget_surgeon')
        **params: Parameters that uniquely identify the request
        
    Returns:
        A SHA-256 hash string
    """
    # Sort params for consistent hashing
    sorted_params = json.dumps(params, sort_keys=True, default=str)
    cache_string = f"{request_type}:{sorted_params}"
    return hashlib.sha256(cache_string.encode()).hexdigest()


def get_cached_response(db: Session, request_hash: str) -> Optional[str]:
    """
    Retrieve a cached response if it exists and hasn't expired.
    
    Args:
        db: Database session
        request_hash: The cache key hash
        
    Returns:
        Cached response string or None if not found/expired
    """
    try:
        cache_entry = db.query(AIRequestCache).filter(
            AIRequestCache.request_hash == request_hash,
            AIRequestCache.expires_at > datetime.utcnow()
        ).first()
        
        if cache_entry:
            # Increment hit count
            cache_entry.hit_count += 1
            db.commit()
            logger.info(f"Cache HIT for hash {request_hash[:8]}... (hits: {cache_entry.hit_count})")
            return cache_entry.response
        
        logger.debug(f"Cache MISS for hash {request_hash[:8]}...")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving cache: {str(e)}")
        return None


def store_cached_response(
    db: Session, 
    request_hash: str, 
    request_type: str,
    prompt: str,
    response: str,
    tokens_used: int = 0
) -> bool:
    """
    Store a response in the cache.
    
    Args:
        db: Database session
        request_hash: The cache key hash
        request_type: Type of AI request
        prompt: The original prompt
        response: The AI response to cache
        tokens_used: Optional token count for tracking
        
    Returns:
        True if stored successfully, False otherwise
    """
    try:
        # Check if entry already exists (upsert)
        existing = db.query(AIRequestCache).filter(
            AIRequestCache.request_hash == request_hash
        ).first()
        
        if existing:
            # Update existing entry
            existing.response = response
            existing.expires_at = AIRequestCache.create_expiry()
            existing.tokens_used = tokens_used
            logger.debug(f"Updated cache entry {request_hash[:8]}...")
        else:
            # Create new entry
            cache_entry = AIRequestCache(
                request_hash=request_hash,
                request_type=request_type,
                prompt=prompt,
                response=response,
                tokens_used=tokens_used,
                expires_at=AIRequestCache.create_expiry()
            )
            db.add(cache_entry)
            logger.debug(f"Created cache entry {request_hash[:8]}...")
        
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error storing cache: {str(e)}")
        db.rollback()
        return False


def get_cache_stats(db: Session) -> dict:
    """
    Get statistics about the AI cache.
    
    Returns:
        Dictionary with cache statistics
    """
    try:
        total_entries = db.query(AIRequestCache).count()
        active_entries = db.query(AIRequestCache).filter(
            AIRequestCache.expires_at > datetime.utcnow()
        ).count()
        total_hits = db.query(AIRequestCache).with_entities(
            db.query(AIRequestCache.hit_count).as_scalar()
        ).scalar() or 0
        
        # Get counts by type
        from sqlalchemy import func
        type_counts = db.query(
            AIRequestCache.request_type,
            func.count(AIRequestCache.id),
            func.sum(AIRequestCache.hit_count)
        ).group_by(AIRequestCache.request_type).all()
        
        by_type = {
            row[0]: {"count": row[1], "hits": row[2] or 0}
            for row in type_counts
        }
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": total_entries - active_entries,
            "by_type": by_type,
            "cache_ttl_hours": settings.ai_cache_ttl / 3600
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return {"error": str(e)}


def clear_expired_cache(db: Session) -> int:
    """
    Clear expired cache entries.
    
    Returns:
        Number of entries deleted
    """
    try:
        deleted = db.query(AIRequestCache).filter(
            AIRequestCache.expires_at <= datetime.utcnow()
        ).delete()
        db.commit()
        logger.info(f"Cleared {deleted} expired cache entries")
        return deleted
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        db.rollback()
        return 0


def clear_all_cache(db: Session) -> int:
    """
    Clear all cache entries.
    
    Returns:
        Number of entries deleted
    """
    try:
        deleted = db.query(AIRequestCache).delete()
        db.commit()
        logger.info(f"Cleared all {deleted} cache entries")
        return deleted
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        db.rollback()
        return 0
