"""Group API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Group, Category
from app.models.activity_log import ActivityLog
from app.schemas import GroupCreate, GroupUpdate, GroupResponse
from app.data_persistence import auto_save

router = APIRouter()


def log_activity(db: Session, action_type: str, entity_type: str, description: str,
                 entity_id: int = None, entity_name: str = None, changes: dict = None,
                 extra_data: dict = None):
    """Helper function to log activity."""
    try:
        ActivityLog.log_action(
            db=db,
            action_type=action_type,
            entity_type=entity_type,
            description=description,
            entity_id=entity_id,
            entity_name=entity_name,
            changes=changes,
            extra_data=extra_data
        )
    except Exception as e:
        # Don't fail the main operation if logging fails
        print(f"Activity logging error: {e}")


@router.post("", response_model=GroupResponse, status_code=201)
def create_group(group: GroupCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new group."""
    # Verify category exists
    category = db.query(Category).filter(Category.id == group.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_group = Group(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    # Log activity
    log_activity(
        db=db,
        action_type="created",
        entity_type="group",
        description=f"Created group '{db_group.name}' in category '{category.name}'",
        entity_id=db_group.id,
        entity_name=db_group.name,
        extra_data={"category_name": category.name}
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_group


@router.get("", response_model=List[GroupResponse])
def list_groups(category_id: int = None, db: Session = Depends(get_db)):
    """List all groups, optionally filtered by category."""
    query = db.query(Group)
    if category_id:
        query = query.filter(Group.category_id == category_id)
    return query.all()


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get a group by ID."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, group: GroupUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update a group."""
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Track changes for activity log
    changes = {}
    update_data = group.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        old_value = getattr(db_group, field)
        if old_value != value:
            changes[field] = {
                "old": str(old_value) if old_value is not None else None,
                "new": str(value) if value is not None else None
            }
        setattr(db_group, field, value)
    
    db.commit()
    db.refresh(db_group)
    
    # Log activity if there were changes
    if changes:
        log_activity(
            db=db,
            action_type="updated",
            entity_type="group",
            description=f"Updated group '{db_group.name}'",
            entity_id=db_group.id,
            entity_name=db_group.name,
            changes=changes
        )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_group


@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Delete a group."""
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Store info for logging before deletion
    group_name = db_group.name
    grp_id = db_group.id
    category_name = db_group.category.name if db_group.category else "Unknown"
    
    db.delete(db_group)
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        action_type="deleted",
        entity_type="group",
        description=f"Deleted group '{group_name}' from category '{category_name}'",
        entity_id=grp_id,
        entity_name=group_name,
        extra_data={"category_name": category_name}
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return None
