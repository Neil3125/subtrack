"""Template API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.database import get_db
from app.models.subscription_template import SubscriptionTemplate
from app.models.subscription import BillingCycle

router = APIRouter()

# Schema
class TemplateBase(BaseModel):
    vendor_name: str
    plan_name: Optional[str] = None
    cost: float
    currency: str = "USD"
    billing_cycle: BillingCycle
    category_id: Optional[int] = None

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[TemplateResponse])
def list_templates(search: Optional[str] = None, db: Session = Depends(get_db)):
    """List all templates, optionally filtering by search query."""
    query = db.query(SubscriptionTemplate)
    if search:
        search_term = f"%{search}%"
        query = query.filter(SubscriptionTemplate.vendor_name.ilike(search_term))
    return query.all()

@router.post("", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template."""
    db_template = SubscriptionTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template: TemplateCreate, db: Session = Depends(get_db)):
    """Update a template."""
    db_template = db.query(SubscriptionTemplate).filter(SubscriptionTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    for key, value in template.model_dump().items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a template."""
    db_template = db.query(SubscriptionTemplate).filter(SubscriptionTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return None
