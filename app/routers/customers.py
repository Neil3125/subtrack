"""Customer API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional
from app.database import get_db
from app.models import Customer, Category, Group
from app.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.data_persistence import auto_save

router = APIRouter()


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new customer with support for multiple categories and groups."""
    
    # Determine which fields to use (new many-to-many or legacy single)
    category_ids = customer.category_ids if customer.category_ids else ([customer.category_id] if customer.category_id else [])
    group_ids = customer.group_ids if customer.group_ids else ([customer.group_id] if customer.group_id else [])
    
    if not category_ids:
        raise HTTPException(status_code=400, detail="At least one category is required")
    
    # Verify all categories exist
    categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
    if len(categories) != len(category_ids):
        raise HTTPException(status_code=404, detail="One or more categories not found")
    
    # Verify all groups exist if provided
    groups = []
    if group_ids:
        groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
        if len(groups) != len(group_ids):
            raise HTTPException(status_code=404, detail="One or more groups not found")
    
    # Create customer with basic fields
    customer_data = customer.model_dump(exclude={'category_id', 'group_id', 'category_ids', 'group_ids'})
    
    # Set legacy fields for backward compatibility (use first category/group)
    customer_data['category_id'] = category_ids[0] if category_ids else None
    customer_data['group_id'] = group_ids[0] if group_ids else None
    
    db_customer = Customer(**customer_data)
    
    # Add many-to-many relationships
    db_customer.categories = categories
    db_customer.groups = groups
    
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_customer


@router.get("/countries", response_model=List[str])
def get_unique_countries(db: Session = Depends(get_db)):
    """Get list of unique countries from all customers."""
    countries = db.query(distinct(Customer.country)).filter(
        Customer.country.isnot(None),
        Customer.country != ""
    ).all()
    return sorted([c[0] for c in countries if c[0]])


@router.get("", response_model=List[CustomerResponse])
def list_customers(
    category_id: Optional[int] = None,
    group_id: Optional[int] = None,
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all customers, optionally filtered by category, group, or country.
    
    Supports both legacy single category/group and new many-to-many relationships.
    """
    query = db.query(Customer)
    
    if category_id:
        # Use legacy field for now (works with or without migration)
        query = query.filter(Customer.category_id == category_id)
    
    if group_id:
        # Use legacy field for now (works with or without migration)
        query = query.filter(Customer.group_id == group_id)
    
    if country:
        query = query.filter(Customer.country == country)
    
    return query.all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a customer by ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer: CustomerUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update a customer with support for multiple categories and groups."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer.model_dump(exclude_unset=True)
    
    # Handle many-to-many relationships separately
    category_ids = update_data.pop('category_ids', None)
    group_ids = update_data.pop('group_ids', None)
    
    # Handle legacy single category/group fields
    legacy_category_id = update_data.pop('category_id', None)
    legacy_group_id = update_data.pop('group_id', None)
    
    # Update basic fields
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    # Update many-to-many relationships if provided
    if category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        if len(categories) != len(category_ids):
            raise HTTPException(status_code=404, detail="One or more categories not found")
        db_customer.categories = categories
        # Update legacy field
        db_customer.category_id = category_ids[0] if category_ids else None
    elif legacy_category_id is not None:
        # Handle legacy single category update
        category = db.query(Category).filter(Category.id == legacy_category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_customer.categories = [category]
        db_customer.category_id = legacy_category_id
    
    if group_ids is not None:
        groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
        if len(groups) != len(group_ids):
            raise HTTPException(status_code=404, detail="One or more groups not found")
        db_customer.groups = groups
        # Update legacy field
        db_customer.group_id = group_ids[0] if group_ids else None
    elif legacy_group_id is not None:
        # Handle legacy single group update
        if legacy_group_id:
            group = db.query(Group).filter(Group.id == legacy_group_id).first()
            if not group:
                raise HTTPException(status_code=404, detail="Group not found")
            db_customer.groups = [group]
            db_customer.group_id = legacy_group_id
        else:
            db_customer.groups = []
            db_customer.group_id = None
    
    db.commit()
    db.refresh(db_customer)
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Delete a customer."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(db_customer)
    db.commit()
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return None
