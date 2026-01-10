"""Category API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    # Check for duplicate
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
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
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return None
