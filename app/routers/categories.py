"""Category API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Category
from app.models.activity_log import ActivityLog
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
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


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new category."""
    # Check for duplicate
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # Log activity
    log_activity(
        db=db,
        action_type="created",
        entity_type="category",
        description=f"Created category '{db_category.name}'",
        entity_id=db_category.id,
        entity_name=db_category.name
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_category


@router.get("", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a category by ID."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category: CategoryUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update a category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Track changes for activity log
    changes = {}
    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        old_value = getattr(db_category, field)
        if old_value != value:
            changes[field] = {
                "old": str(old_value) if old_value is not None else None,
                "new": str(value) if value is not None else None
            }
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    # Log activity if there were changes
    if changes:
        log_activity(
            db=db,
            action_type="updated",
            entity_type="category",
            description=f"Updated category '{db_category.name}'",
            entity_id=db_category.id,
            entity_name=db_category.name,
            changes=changes
        )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Delete a category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Store info for logging before deletion
    category_name = db_category.name
    cat_id = db_category.id
    
    db.delete(db_category)
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        action_type="deleted",
        entity_type="category",
        description=f"Deleted category '{category_name}'",
        entity_id=cat_id,
        entity_name=category_name
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return None
