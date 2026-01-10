"""Subscription API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Subscription, Customer, Category
from app.schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse

router = APIRouter()


@router.post("", response_model=SubscriptionResponse, status_code=201)
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    """Create a new subscription."""
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == subscription.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == subscription.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_subscription = Subscription(**subscription.model_dump())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.get("", response_model=List[SubscriptionResponse])
def list_subscriptions(
    customer_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all subscriptions, with optional filters."""
    query = db.query(Subscription)
    if customer_id:
        query = query.filter(Subscription.customer_id == customer_id)
    if category_id:
        query = query.filter(Subscription.category_id == category_id)
    if status:
        query = query.filter(Subscription.status == status)
    return query.all()


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Get a subscription by ID."""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(subscription_id: int, subscription: SubscriptionUpdate, db: Session = Depends(get_db)):
    """Update a subscription."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    update_data = subscription.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subscription, field, value)
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.delete("/{subscription_id}", status_code=204)
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Delete a subscription."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(db_subscription)
    db.commit()
    return None
