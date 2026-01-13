"""Customer API routes."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import logging
import re
from app.database import get_db
from app.models import Customer, Category, Group
from app.models.activity_log import ActivityLog
from app.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.data_persistence import auto_save

# Set up logging for debugging
logger = logging.getLogger(__name__)

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
        logger.error(f"Activity logging error: {e}")


def validate_email_format(email: str) -> bool:
    """Validate email format using regex."""
    if not email:
        return True  # Empty email is valid (optional field)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new customer.
    
    Supports multiple groups via group_ids array. Also accepts legacy group_id field.
    All specified groups will be saved using the many-to-many relationship.
    """
    
    # Log incoming request (redact sensitive data)
    logger.info(f"Creating customer: name={customer.name}, category_id={customer.category_id}, country={customer.country}")
    
    # Validate required fields with clear messages
    validation_errors = []
    
    if not customer.name or not customer.name.strip():
        validation_errors.append("Customer name is required")
    
    if not customer.country or not customer.country.strip():
        validation_errors.append("Country is required")
    
    # Validate email format if provided
    if customer.email and not validate_email_format(customer.email):
        validation_errors.append(f"Invalid email format: {customer.email}")
    
    # Determine category - prefer single value, fall back to arrays
    category_id = customer.category_id
    if not category_id and customer.category_ids:
        category_id = customer.category_ids[0] if customer.category_ids else None
    
    # Collect all group IDs - support both single and multiple
    group_ids = []
    if customer.group_ids:
        group_ids = list(customer.group_ids)
    elif customer.group_id:
        group_ids = [customer.group_id]
    
    # Remove duplicates while preserving order
    group_ids = list(dict.fromkeys(group_ids))
    
    if not category_id:
        validation_errors.append("Category is required")
    
    # Return all validation errors at once
    if validation_errors:
        error_message = "; ".join(validation_errors)
        logger.warning(f"Validation failed for customer creation: {error_message}")
        raise HTTPException(status_code=400, detail=error_message)
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        logger.warning(f"Category not found: {category_id}")
        raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
    
    # Verify all groups exist if provided
    groups = []
    if group_ids:
        groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
        if len(groups) != len(group_ids):
            found_ids = {g.id for g in groups}
            missing_ids = [gid for gid in group_ids if gid not in found_ids]
            logger.warning(f"Groups not found: {missing_ids}")
            raise HTTPException(status_code=404, detail=f"Groups with IDs {missing_ids} not found")
    
    # Check for duplicate customer (same name + email in same category)
    if customer.email:
        existing_customer = db.query(Customer).filter(
            Customer.email == customer.email,
            Customer.category_id == category_id
        ).first()
        if existing_customer:
            logger.warning(f"Duplicate customer: email {customer.email} already exists in category {category_id}")
            raise HTTPException(
                status_code=409, 
                detail=f"A customer with email '{customer.email}' already exists in this category"
            )
    
    try:
        # Create customer with basic fields
        customer_data = customer.model_dump(exclude={'category_id', 'group_id', 'category_ids', 'group_ids'})
        
        # Set the category_id
        customer_data['category_id'] = category_id
        # Set legacy group_id to first group for backward compatibility
        customer_data['group_id'] = group_ids[0] if group_ids else None
        
        db_customer = Customer(**customer_data)
        
        # Set many-to-many groups relationship
        if groups:
            db_customer.set_groups(groups)
        
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        
        group_names = ", ".join([g.name for g in groups]) if groups else "None"
        logger.info(f"Customer created successfully: id={db_customer.id}, name={db_customer.name}, groups=[{group_names}]")
        
        # Log activity
        log_activity(
            db=db,
            action_type="created",
            entity_type="customer",
            description=f"Created customer '{db_customer.name}'",
            entity_id=db_customer.id,
            entity_name=db_customer.name,
            extra_data={"email": db_customer.email, "country": db_customer.country, "category": category.name, "groups": group_names}
        )
        
        # Auto-save data to file
        background_tasks.add_task(auto_save, db)
        
        return db_customer
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating customer: {str(e)}")
        raise HTTPException(
            status_code=409, 
            detail="A customer with this information already exists or database constraint violated"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating customer: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create customer: {str(e)}"
        )


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
    """Update a customer with support for multiple groups.
    
    Supports multiple groups via group_ids array. All specified groups will be saved
    using the many-to-many relationship. Also maintains backward compatibility with
    the legacy group_id field.
    """
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Store original values for change tracking
    original_group_names = db_customer.group_names
    original_values = {
        "name": db_customer.name,
        "email": db_customer.email,
        "phone": db_customer.phone,
        "country": db_customer.country,
        "tags": db_customer.tags,
        "notes": db_customer.notes,
        "category_id": db_customer.category_id,
        "groups": original_group_names
    }
    
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
    
    # Handle category update - prefer category_ids array, fall back to legacy
    if category_ids is not None and len(category_ids) > 0:
        # Verify categories exist
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        if len(categories) != len(category_ids):
            raise HTTPException(status_code=404, detail="One or more categories not found")
        # Use first category as primary (legacy field)
        db_customer.category_id = category_ids[0]
    elif legacy_category_id is not None:
        # Handle legacy single category update
        category = db.query(Category).filter(Category.id == legacy_category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_customer.category_id = legacy_category_id
    
    # Handle group update - prefer group_ids array, fall back to legacy
    if group_ids is not None:
        if len(group_ids) > 0:
            # Remove duplicates while preserving order
            group_ids = list(dict.fromkeys(group_ids))
            # Verify all groups exist
            groups = db.query(Group).filter(Group.id.in_(group_ids)).all()
            if len(groups) != len(group_ids):
                found_ids = {g.id for g in groups}
                missing_ids = [gid for gid in group_ids if gid not in found_ids]
                raise HTTPException(status_code=404, detail=f"Groups with IDs {missing_ids} not found")
            # Set many-to-many groups relationship
            db_customer.set_groups(groups)
        else:
            # Empty array means remove from all groups
            db_customer.set_groups([])
    elif legacy_group_id is not None:
        # Handle legacy single group update
        if legacy_group_id:
            group = db.query(Group).filter(Group.id == legacy_group_id).first()
            if not group:
                raise HTTPException(status_code=404, detail="Group not found")
            db_customer.set_groups([group])
        else:
            db_customer.set_groups([])
    
    db.commit()
    db.refresh(db_customer)
    
    # Track changes for activity log
    changes = {}
    new_group_names = db_customer.group_names
    new_values = {
        "name": db_customer.name,
        "email": db_customer.email,
        "phone": db_customer.phone,
        "country": db_customer.country,
        "tags": db_customer.tags,
        "notes": db_customer.notes,
        "category_id": db_customer.category_id,
        "groups": new_group_names
    }
    for field, old_value in original_values.items():
        new_value = new_values.get(field)
        if old_value != new_value:
            changes[field] = {
                "old": str(old_value) if old_value is not None else None,
                "new": str(new_value) if new_value is not None else None
            }
    
    # Log activity if there were changes
    if changes:
        log_activity(
            db=db,
            action_type="updated",
            entity_type="customer",
            description=f"Updated customer '{db_customer.name}'",
            entity_id=db_customer.id,
            entity_name=db_customer.name,
            changes=changes
        )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return db_customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Delete a customer."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Store info for logging before deletion
    customer_name = db_customer.name
    cust_id = db_customer.id
    customer_email = db_customer.email
    category_name = db_customer.category.name if db_customer.category else "Unknown"
    
    db.delete(db_customer)
    db.commit()
    
    # Log activity
    log_activity(
        db=db,
        action_type="deleted",
        entity_type="customer",
        description=f"Deleted customer '{customer_name}'",
        entity_id=cust_id,
        entity_name=customer_name,
        extra_data={"email": customer_email, "category": category_name}
    )
    
    # Auto-save data to file
    background_tasks.add_task(auto_save, db)
    
    return None
