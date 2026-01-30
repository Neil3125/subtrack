from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import SubscriptionTemplate
from app.schemas import SubscriptionTemplateCreate, SubscriptionTemplateUpdate, SubscriptionTemplateResponse
from app.data_persistence import auto_save

router = APIRouter()

@router.get("", response_model=List[SubscriptionTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    """List all subscription templates."""
    return db.query(SubscriptionTemplate).all()

@router.post("", response_model=SubscriptionTemplateResponse, status_code=201)
def create_template(template: SubscriptionTemplateCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new subscription template."""
    db_template = SubscriptionTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    background_tasks.add_task(auto_save, db)
    return db_template

@router.put("/{template_id}", response_model=SubscriptionTemplateResponse)
def update_template(template_id: int, template_update: SubscriptionTemplateUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update a subscription template."""
    db_template = db.query(SubscriptionTemplate).filter(SubscriptionTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)
        
    db.commit()
    db.refresh(db_template)
    
    background_tasks.add_task(auto_save, db)
    return db_template

@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Delete a subscription template."""
    db_template = db.query(SubscriptionTemplate).filter(SubscriptionTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    db.delete(db_template)
    db.commit()
    
    background_tasks.add_task(auto_save, db)
    return None
