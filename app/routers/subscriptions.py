"""Subscription API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models import Subscription, Customer, Category
from app.models.subscription_template import SubscriptionTemplate
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

    # Determine category IDs to apply (multi-select preferred)
    category_ids: List[int] = []
    if subscription.category_ids and len(subscription.category_ids) > 0:
        category_ids = list(subscription.category_ids)
    elif subscription.category_id is not None:
        category_ids = [subscription.category_id]
    else:
        raise HTTPException(status_code=422, detail="At least one category is required")

    # Validate categories exist
    categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
    if len(categories) != len(set(category_ids)):
        raise HTTPException(status_code=404, detail="One or more categories not found")

    # Primary category stays as first category for backward compatibility
    primary_category_id = category_ids[0]

    # Create subscription (exclude category_ids and save_template)
    payload = subscription.model_dump(exclude={"category_ids", "save_template"})
    payload["category_id"] = primary_category_id

    db_subscription = Subscription(**payload)
    # Persist many-to-many relationship
    db_subscription.categories = categories

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
        extra_data={
            "customer_name": customer.name,
            "cost": str(db_subscription.cost),
            "currency": db_subscription.currency,
            "category_ids": category_ids,
        }
    )

    # Auto-save data to file
    background_tasks.add_task(auto_save, db)

    # Save as template if requested
    if subscription.save_template:
        try:
            # Check if template already exists to avoid duplicates
            existing = db.query(SubscriptionTemplate).filter(
                SubscriptionTemplate.vendor_name == db_subscription.vendor_name,
                SubscriptionTemplate.plan_name == db_subscription.plan_name
            ).first()
            
            if not existing:
                template = SubscriptionTemplate(
                    vendor_name=db_subscription.vendor_name,
                    plan_name=db_subscription.plan_name,
                    cost=db_subscription.cost,
                    currency=db_subscription.currency,
                    billing_cycle=db_subscription.billing_cycle,
                    category_id=primary_category_id
                )
                db.add(template)
                db.commit()
                print(f"Template auto-saved for {db_subscription.vendor_name}")
        except Exception as e:
            print(f"Error saving template: {e}")

    # Ensure response includes category_ids
    setattr(db_subscription, "category_ids", [c.id for c in db_subscription.categories] if db_subscription.categories else [db_subscription.category_id])

    return db_subscription


@router.get("", response_model=List[SubscriptionResponse])
def list_subscriptions(
    customer_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """List all subscriptions, with optional filters."""
    query = db.query(Subscription)
    if customer_id:
        query = query.filter(Subscription.customer_id == customer_id)
    if category_id:
        # Filter by primary category for backward compatibility
        query = query.filter(Subscription.category_id == category_id)
    if status:
        query = query.filter(Subscription.status == status)
    
    # Date range filtering for calendar
    if start_date:
        query = query.filter(Subscription.next_renewal_date >= start_date)
    if end_date:
        query = query.filter(Subscription.next_renewal_date <= end_date)

    subs = query.all()
    # Attach category_ids for response serialization
    for s in subs:
        try:
            setattr(s, "category_ids", [c.id for c in s.categories] if getattr(s, "categories", None) else [s.category_id])
        except Exception:
            setattr(s, "category_ids", [s.category_id])
    return subs


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Get a subscription by ID."""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    setattr(subscription, "category_ids", [c.id for c in subscription.categories] if getattr(subscription, "categories", None) else [subscription.category_id])
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

    # Handle category_ids (many-to-many)
    if "category_ids" in update_data:
        category_ids = update_data.pop("category_ids") or []
        if len(category_ids) > 0:
            categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
            if len(categories) != len(set(category_ids)):
                raise HTTPException(status_code=404, detail="One or more categories not found")

            db_subscription.categories = categories
            # Also update primary category for backward compatibility
            db_subscription.category_id = category_ids[0]
            changes["category_ids"] = {
                "old": str([c.id for c in db_subscription.categories]) if db_subscription.categories else None,
                "new": str(category_ids)
            }
        else:
            # Allow clearing all categories? Keep at least primary category for compatibility
            pass

    for field, value in update_data.items():
        old_value = getattr(db_subscription, field)
        if old_value != value:
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

    setattr(db_subscription, "category_ids", [c.id for c in db_subscription.categories] if getattr(db_subscription, "categories", None) else [db_subscription.category_id])
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
@router.get("/templates/all", response_model=List[dict])
def get_subscription_templates(search: Optional[str] = None, db: Session = Depends(get_db)):
    """Get a list of subscription templates (vendor/plan combinations)."""
    try:
        query = db.query(SubscriptionTemplate)
        
        if search:
            query = query.filter(SubscriptionTemplate.vendor_name.ilike(f"%{search}%"))
            
        templates = query.order_by(SubscriptionTemplate.vendor_name).all()
        
        # Format as expected by frontend
        results = []
        for t in templates:
            results.append({
                "id": t.id,
                "vendor_name": t.vendor_name,
                "plan_name": t.plan_name,
                "cost": t.cost,
                "currency": t.currency,
                "billing_cycle": t.billing_cycle,
                "category_id": t.category_id,
                "label": f"{t.vendor_name} {f'- {t.plan_name}' if t.plan_name else ''} ({t.currency} {t.cost})"
            })
            
        return results
    except Exception as e:
        print(f"Error fetching templates: {e}")
        return []
@router.get("/stats/vendors", response_model=List[dict])
def get_vendor_stats(db: Session = Depends(get_db)):
    """
    Get aggregated statistics for vendors to support smart autofill.
    Returns most frequent settings for each vendor based on history.
    """
    # Query all active or past subscriptions
    subs = db.query(Subscription).all()
    
    if not subs:
        return []

    from collections import Counter, defaultdict
    
    # Group by vendor
    vendor_groups = defaultdict(list)
    for sub in subs:
        if sub.vendor_name:
            vendor_groups[sub.vendor_name].append(sub)
    
    results = []
    
    for vendor_name, vendor_subs in vendor_groups.items():
        if not vendor_subs:
            continue
            
        # Helper to find mode
        def get_mode(items):
            if not items: return None
            return Counter(items).most_common(1)[0][0]
        
        # Calculate stats
        costs = [s.cost for s in vendor_subs]
        currencies = [s.currency for s in vendor_subs if s.currency]
        cycles = [s.billing_cycle for s in vendor_subs if s.billing_cycle]
        plans = [s.plan_name for s in vendor_subs if s.plan_name]
        category_ids = [s.category_id for s in vendor_subs if s.category_id]
        
        # Determine average cost (maybe better than mode for cost?)
        # Let's use Mode for consistency, or Average if variance is low?
        # Plan says "Most frequent or Average". Let's use Mode for cost to hit exact price points (e.g. 15.99)
        default_cost = get_mode(costs)
        
        # Create stat object
        stat = {
            "name": vendor_name,
            "count": len(vendor_subs),
            "category_id": get_mode(category_ids),
            "cost": default_cost,
            "currency": get_mode(currencies) or "USD",
            "billing_cycle": get_mode(cycles),
            "plan_name": get_mode(plans)
        }
        results.append(stat)
        
    # Sort by frequency
    results.sort(key=lambda x: x['count'], reverse=True)
    
    return results
