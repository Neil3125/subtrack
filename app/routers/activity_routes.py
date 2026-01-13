"""Activity log routes for tracking and displaying user actions."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.activity_log import ActivityLog

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("/logs")
def get_activity_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    entity_type: Optional[str] = None,
    action_type: Optional[str] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get activity logs with optional filtering.
    
    Args:
        page: Page number (1-indexed)
        limit: Number of items per page
        entity_type: Filter by entity type (subscription, customer, etc.)
        action_type: Filter by action type (created, updated, deleted, etc.)
        days: Filter to only show logs from the last N days
    """
    query = db.query(ActivityLog)
    
    # Apply filters
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if action_type:
        query = query.filter(ActivityLog.action_type == action_type)
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(ActivityLog.created_at >= cutoff_date)
    
    # Get total count
    total = query.count()
    
    # Order by most recent and paginate
    logs = query.order_by(desc(ActivityLog.created_at)).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "action_type": log.action_type,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "entity_name": log.entity_name,
                "description": log.description,
                "changes": log.changes,
                "metadata": log.metadata,
                "icon": log.icon
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/stats")
def get_activity_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get activity statistics for the dashboard."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(ActivityLog).filter(ActivityLog.created_at >= cutoff_date)
    
    logs = query.all()
    
    # Count by action type
    action_counts = {}
    entity_counts = {}
    
    for log in logs:
        action_counts[log.action_type] = action_counts.get(log.action_type, 0) + 1
        entity_counts[log.entity_type] = entity_counts.get(log.entity_type, 0) + 1
    
    return {
        "total_actions": len(logs),
        "action_counts": action_counts,
        "entity_counts": entity_counts,
        "period_days": days
    }


@router.delete("/logs/{log_id}")
def delete_activity_log(log_id: int, db: Session = Depends(get_db)):
    """Delete a specific activity log entry (admin only)."""
    log = db.query(ActivityLog).filter(ActivityLog.id == log_id).first()
    if not log:
        return {"error": "Log not found"}
    
    db.delete(log)
    db.commit()
    return {"success": True}


@router.delete("/logs")
def clear_old_logs(
    days: int = Query(30, ge=0),
    db: Session = Depends(get_db)
):
    """Clear activity logs older than specified days. Use days=0 to clear all logs."""
    if days == 0:
        # Clear all logs
        deleted = db.query(ActivityLog).delete()
    else:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(ActivityLog).filter(ActivityLog.created_at < cutoff_date).delete()
    
    db.commit()
    
    return {"deleted_count": deleted}
