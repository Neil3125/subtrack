"""Activity log model for tracking user actions and changes."""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ActivityLog(Base):
    """Model for tracking all user activities and changes in the system.
    
    This provides a comprehensive audit trail of actions taken including:
    - Create, update, delete operations on all entities
    - Email notifications sent
    - Subscription renewals
    - Status changes
    """
    
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # When the action occurred
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # What type of action was performed
    action_type = Column(String(50), nullable=False, index=True)
    # Values: created, updated, deleted, email_sent, renewed, status_changed, bulk_email_sent
    
    # What entity was affected
    entity_type = Column(String(50), nullable=False, index=True)
    # Values: subscription, customer, category, group, user
    
    entity_id = Column(Integer, nullable=True, index=True)
    
    # Human-readable description of the action
    description = Column(Text, nullable=False)
    
    # Detailed changes (for updates) - stores before/after values as JSON
    changes = Column(JSON, nullable=True)
    # Format: {"field_name": {"old": "old_value", "new": "new_value"}, ...}
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    # Can store things like: email recipient, subscription vendor name, etc.
    
    # User who performed the action (if applicable)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="activity_logs")
    
    # Related entity names for display (so we don't need to join)
    entity_name = Column(String(255), nullable=True)
    
    # Icon/badge for UI display
    icon = Column(String(10), nullable=True)
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action={self.action_type}, entity={self.entity_type}, created_at={self.created_at})>"
    
    @classmethod
    def log_action(cls, db, action_type: str, entity_type: str, description: str, 
                   entity_id: int = None, entity_name: str = None, changes: dict = None,
                   metadata: dict = None, user_id: int = None, icon: str = None):
        """
        Helper method to create a new activity log entry.
        
        Args:
            db: Database session
            action_type: Type of action (created, updated, deleted, email_sent, etc.)
            entity_type: Type of entity affected (subscription, customer, etc.)
            description: Human-readable description
            entity_id: ID of the affected entity
            entity_name: Name of the affected entity for display
            changes: Dict of field changes with old/new values
            metadata: Additional metadata
            user_id: ID of user who performed the action
            icon: Emoji icon for display
        
        Returns:
            The created ActivityLog instance
        """
        # Auto-assign icons based on action type if not provided
        if icon is None:
            icon_map = {
                'created': '➕',
                'updated': '✏️',
                'deleted': '🗑️',
                'email_sent': '📧',
                'bulk_email_sent': '📨',
                'renewed': '🔄',
                'status_changed': '🔀',
                'imported': '📥',
                'exported': '📤',
            }
            icon = icon_map.get(action_type, '📋')
        
        log_entry = cls(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            changes=changes,
            metadata=metadata,
            user_id=user_id,
            icon=icon
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return log_entry
