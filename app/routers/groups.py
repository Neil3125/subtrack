"""Group API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Group, Category
from app.schemas import GroupCreate, GroupUpdate, GroupResponse
from app.data_persistence import auto_save

router = APIRouter()


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
    
    update_data = group.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_group, field, value)
    
    db.commit()
    db.refresh(db_group)
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_group


@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Delete a group."""
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    db.delete(db_group)
    db.commit()
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return None
