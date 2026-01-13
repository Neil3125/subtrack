"""Subscription API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Subscription, Customer, Category
from app.models.activity_log import ActivityLog
from app.schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
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


@router.post("", response_model=SubscriptionResponse, status_code=201)
def create_subscription(subscription: SubscriptionCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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
    
    # Log activity
    log_activity(
        db=db,
        action_type="created",
        entity_type="subscription",
        description=f"Created subscription '{db_subscription.vendor_name}' for {customer.name}",
        entity_id=db_subscription.id,
        entity_name=db_subscription.vendor_name,
        extra_data={"customer_name": customer.name, "cost": str(db_subscription.cost), "currency": db_subscription.currency}
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
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
def update_subscription(subscription_id: int, subscription: SubscriptionUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Update a subscription."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Track changes for activity log
    changes = {}
    update_data = subscription.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        old_value = getattr(db_subscription, field)
        if old_value != value:
            # Convert to string for JSON serialization
            changes[field] = {
                "old": str(old_value) if old_value is not None else None,
                "new": str(value) if value is not None else None
            }
        setattr(db_subscription, field, value)
    
    db.commit()
    db.refresh(db_subscription)
    
    # Log activity if there were changes
    if changes:
        log_activity(
            db=db,
            action_type="updated",
            entity_type="subscription",
            description=f"Updated subscription '{db_subscription.vendor_name}'",
            entity_id=db_subscription.id,
            entity_name=db_subscription.vendor_name,
            changes=changes
        )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_subscription


@router.delete("/{subscription_id}", status_code=204)
def delete_subscription(subscription_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Delete a subscription."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Store info for logging before deletion
    vendor_name = db_subscription.vendor_name
    sub_id = db_subscription.id
    customer_name = db_subscription.customer.name if db_subscription.customer else "Unknown"
    
    db.delete(db_subscription)
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        action_type="deleted",
        entity_type="subscription",
        description=f"Deleted subscription '{vendor_name}' from {customer_name}",
        entity_id=sub_id,
        entity_name=vendor_name,
        extra_data={"customer_name": customer_name}
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return None


@router.post("/{subscription_id}/renew")
def renew_subscription(subscription_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Renew a subscription to the next billing cycle."""
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta
    from app.models.subscription import SubscriptionStatus
    
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Store old date for logging
    old_date = db_subscription.next_renewal_date
    
    # Calculate next renewal date based on billing cycle
    current_date = db_subscription.next_renewal_date or date.today()
    
    if db_subscription.billing_cycle.value == 'weekly':
        new_date = current_date + timedelta(weeks=1)
    elif db_subscription.billing_cycle.value == 'monthly':
        new_date = current_date + relativedelta(months=1)
    elif db_subscription.billing_cycle.value == 'quarterly':
        new_date = current_date + relativedelta(months=3)
    elif db_subscription.billing_cycle.value == 'biannual':
        new_date = current_date + relativedelta(months=6)
    elif db_subscription.billing_cycle.value == 'yearly':
        new_date = current_date + relativedelta(years=1)
    else:
        new_date = current_date + relativedelta(months=1)
    
    db_subscription.next_renewal_date = new_date
    db_subscription.status = SubscriptionStatus.ACTIVE
    
    db.commit()
    db.refresh(db_subscription)
    
    # Log activity
    customer_name = db_subscription.customer.name if db_subscription.customer else "Unknown"
    log_activity(
        db=db,
        action_type="renewed",
        entity_type="subscription",
        description=f"Renewed subscription '{db_subscription.vendor_name}' for {customer_name}",
        entity_id=db_subscription.id,
        entity_name=db_subscription.vendor_name,
        changes={
            "next_renewal_date": {
                "old": old_date.isoformat() if old_date else None,
                "new": new_date.isoformat()
            }
        },
        extra_data={"customer_name": customer_name, "billing_cycle": db_subscription.billing_cycle.value}
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return {
        "message": "Subscription renewed",
        "next_renewal_date": new_date.isoformat()
    }
