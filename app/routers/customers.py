"""Customer API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional
from app.database import get_db
from app.models import Customer, Category, Group
from app.schemas import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter()


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    # Verify category exists
    category = db.query(Category).filter(Category.id == customer.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Verify group exists if provided
    if customer.group_id:
        group = db.query(Group).filter(Group.id == customer.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
    
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
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
    """List all customers, optionally filtered by category, group, or country."""
    query = db.query(Customer)
    if category_id:
        query = query.filter(Customer.category_id == category_id)
    if group_id:
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
def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Delete a customer."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(db_customer)
    db.commit()
    return None
