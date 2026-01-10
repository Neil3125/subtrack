"""
Automatic Data Persistence Module for SubTrack.

This module ensures that data survives code deployments by:
1. Auto-exporting data to a JSON file after any write operation
2. Auto-importing data from JSON on startup if the database is empty
3. Supporting environment variable storage for platforms with ephemeral filesystems

For Railway/Render/Heroku deployments:
- Set SUBTRACK_DATA environment variable with base64-encoded JSON data
- The app will auto-restore from this on startup
- Use the /api/export/data-string endpoint to get the current data string
"""
import json
import os
import base64
import threading
from datetime import datetime, date
from typing import Optional
from contextlib import contextmanager
from sqlalchemy.orm import Session

# File for persistent data storage
DATA_FILE = "subtrack_data.json"
BACKUP_DATA_FILE = "subtrack_data_backup.json"

# Environment variable for data persistence (base64 encoded JSON)
DATA_ENV_VAR = "SUBTRACK_DATA"

# Lock to prevent concurrent writes
_write_lock = threading.Lock()

# Flag to prevent recursive saves during import
_importing = False


def datetime_handler(obj):
    """JSON serializer for datetime objects."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def export_all_data(db: Session) -> dict:
    """Export all data from database to a dictionary."""
    from app.models import Category, Group, Customer, Subscription, Link
    from app.models.saved_report import SavedReport
    from sqlalchemy import text
    
    data = {
        "exported_at": datetime.now().isoformat(),
        "categories": [],
        "groups": [],
        "customers": [],
        "subscriptions": [],
        "links": [],
        "saved_reports": []
    }
    
    # Export categories
    try:
        for cat in db.query(Category).all():
            data["categories"].append({
                "id": cat.id,
                "name": cat.name,
                "description": cat.description
            })
    except Exception as e:
        print(f"[DataPersistence] Error exporting categories: {e}")
    
    # Export groups
    try:
        for group in db.query(Group).all():
            data["groups"].append({
                "id": group.id,
                "category_id": group.category_id,
                "name": group.name,
                "notes": group.notes
            })
    except Exception as e:
        print(f"[DataPersistence] Error exporting groups: {e}")
    
    # Export customers - use raw SQL to handle missing columns
    try:
        # First check which columns exist
        result = db.execute(text("PRAGMA table_info(customers)")).fetchall()
        columns = [row[1] for row in result]
        has_country = 'country' in columns
        
        # Build column list dynamically
        base_cols = "id, category_id, group_id, name, email, phone, tags, notes"
        if has_country:
            base_cols += ", country"
        
        rows = db.execute(text(f"SELECT {base_cols} FROM customers")).fetchall()
        for row in rows:
            customer_data = {
                "id": row[0],
                "category_id": row[1],
                "group_id": row[2],
                "name": row[3],
                "email": row[4],
                "phone": row[5],
                "tags": row[6],
                "notes": row[7]
            }
            # Include country if column exists
            if has_country:
                customer_data["country"] = row[8] if len(row) > 8 else None
            data["customers"].append(customer_data)
    except Exception as e:
        print(f"[DataPersistence] Error exporting customers: {e}")
    
    # Export subscriptions - use raw SQL to handle missing columns
    try:
        # First check which columns exist
        result = db.execute(text("PRAGMA table_info(subscriptions)")).fetchall()
        columns = [row[1] for row in result]
        has_country = 'country' in columns
        
        # Build column list dynamically
        base_cols = "id, customer_id, category_id, vendor_name, plan_name, cost, currency, billing_cycle, start_date, next_renewal_date, status, notes"
        if has_country:
            base_cols += ", country"
        
        rows = db.execute(text(f"SELECT {base_cols} FROM subscriptions")).fetchall()
        for row in rows:
            sub_data = {
                "id": row[0],
                "customer_id": row[1],
                "category_id": row[2],
                "vendor_name": row[3],
                "plan_name": row[4],
                "cost": float(row[5]) if row[5] else 0,
                "currency": row[6],
                "billing_cycle": row[7] if row[7] else "monthly",
                "start_date": row[8] if row[8] else None,
                "next_renewal_date": row[9] if row[9] else None,
                "status": row[10] if row[10] else "active",
                "notes": row[11]
            }
            # Include country if column exists
            if has_country:
                sub_data["country"] = row[12] if len(row) > 12 else None
            data["subscriptions"].append(sub_data)
    except Exception as e:
        print(f"[DataPersistence] Error exporting subscriptions: {e}")
    
    # Export links
    try:
        for link in db.query(Link).all():
            data["links"].append({
                "id": link.id,
                "subscription_id": link.subscription_id,
                "title": link.title,
                "url": link.url,
                "link_type": link.link_type,
                "notes": link.notes
            })
    except Exception:
        # Links table might not exist
        pass
    
    # Export saved reports
    try:
        for report in db.query(SavedReport).all():
            data["saved_reports"].append({
                "id": report.id,
                "name": report.name,
                "report_type": report.report_type,
                "filters": report.filters,
                "created_at": report.created_at.isoformat() if report.created_at else None
            })
    except Exception:
        # SavedReport table might not exist
        pass
    
    return data


def save_data_to_file(data: dict, filename: str = DATA_FILE) -> bool:
    """Save data dictionary to JSON file."""
    global _importing
    
    if _importing:
        return False
    
    with _write_lock:
        try:
            # Create backup of existing file
            if os.path.exists(filename):
                backup_name = BACKUP_DATA_FILE
                try:
                    with open(filename, 'r') as f:
                        existing = f.read()
                    with open(backup_name, 'w') as f:
                        f.write(existing)
                except Exception:
                    pass
            
            # Write new data
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=datetime_handler)
            
            return True
        except Exception as e:
            print(f"[DataPersistence] Error saving data: {e}")
            return False


def load_data_from_env() -> Optional[dict]:
    """Load data from environment variable (base64 encoded JSON)."""
    env_data = os.environ.get(DATA_ENV_VAR)
    if not env_data:
        return None
    
    try:
        # Decode base64 and parse JSON
        json_str = base64.b64decode(env_data).decode('utf-8')
        data = json.loads(json_str)
        print(f"[DataPersistence] Loaded data from environment variable")
        return data
    except Exception as e:
        print(f"[DataPersistence] Error loading data from env var: {e}")
        return None


def load_data_from_file(filename: str = DATA_FILE) -> Optional[dict]:
    """Load data dictionary from JSON file."""
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[DataPersistence] Error loading data from {filename}: {e}")
        # Try backup
        if os.path.exists(BACKUP_DATA_FILE):
            try:
                with open(BACKUP_DATA_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None


def load_data() -> Optional[dict]:
    """
    Load data from the best available source.
    Priority: 1) Environment variable, 2) JSON file, 3) Backup file
    """
    # First try environment variable (for Railway/Render deployments)
    data = load_data_from_env()
    if data:
        return data
    
    # Then try JSON file
    data = load_data_from_file()
    if data:
        return data
    
    return None


def get_data_as_base64(db: Session) -> str:
    """
    Export current data as base64 string for environment variable storage.
    Use this to get the string to set as SUBTRACK_DATA env var.
    """
    data = export_all_data(db)
    json_str = json.dumps(data, default=datetime_handler)
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')


def import_data_to_db(db: Session, data: dict) -> bool:
    """Import data from dictionary to database."""
    global _importing
    
    from app.models import Category, Group, Customer, Subscription, Link
    from app.models.subscription import BillingCycle, SubscriptionStatus
    from app.models.saved_report import SavedReport
    
    _importing = True
    
    try:
        # Import categories
        for cat_data in data.get("categories", []):
            existing = db.query(Category).filter(Category.id == cat_data["id"]).first()
            if not existing:
                cat = Category(
                    id=cat_data["id"],
                    name=cat_data["name"],
                    description=cat_data.get("description")
                )
                db.add(cat)
        db.commit()
        
        # Import groups
        for group_data in data.get("groups", []):
            existing = db.query(Group).filter(Group.id == group_data["id"]).first()
            if not existing:
                group = Group(
                    id=group_data["id"],
                    category_id=group_data["category_id"],
                    name=group_data["name"],
                    notes=group_data.get("notes")
                )
                db.add(group)
        db.commit()
        
        # Import customers
        for customer_data in data.get("customers", []):
            existing = db.query(Customer).filter(Customer.id == customer_data["id"]).first()
            if not existing:
                customer = Customer(
                    id=customer_data["id"],
                    category_id=customer_data["category_id"],
                    group_id=customer_data.get("group_id"),
                    name=customer_data["name"],
                    email=customer_data.get("email"),
                    phone=customer_data.get("phone"),
                    tags=customer_data.get("tags"),
                    notes=customer_data.get("notes")
                )
                # Set country if available
                if "country" in customer_data and hasattr(customer, 'country'):
                    customer.country = customer_data["country"]
                db.add(customer)
        db.commit()
        
        # Import subscriptions
        for sub_data in data.get("subscriptions", []):
            existing = db.query(Subscription).filter(Subscription.id == sub_data["id"]).first()
            if not existing:
                sub = Subscription(
                    id=sub_data["id"],
                    customer_id=sub_data["customer_id"],
                    category_id=sub_data["category_id"],
                    vendor_name=sub_data["vendor_name"],
                    plan_name=sub_data.get("plan_name"),
                    cost=sub_data.get("cost", 0),
                    currency=sub_data.get("currency", "USD"),
                    billing_cycle=BillingCycle(sub_data.get("billing_cycle", "monthly")),
                    start_date=datetime.fromisoformat(sub_data["start_date"]).date() if sub_data.get("start_date") else None,
                    next_renewal_date=datetime.fromisoformat(sub_data["next_renewal_date"]).date() if sub_data.get("next_renewal_date") else None,
                    status=SubscriptionStatus(sub_data.get("status", "active")),
                    notes=sub_data.get("notes")
                )
                # Set country if available
                if "country" in sub_data and hasattr(sub, 'country'):
                    sub.country = sub_data["country"]
                db.add(sub)
        db.commit()
        
        # Import links
        for link_data in data.get("links", []):
            try:
                existing = db.query(Link).filter(Link.id == link_data["id"]).first()
                if not existing:
                    link = Link(
                        id=link_data["id"],
                        subscription_id=link_data["subscription_id"],
                        title=link_data.get("title"),
                        url=link_data["url"],
                        link_type=link_data.get("link_type"),
                        notes=link_data.get("notes")
                    )
                    db.add(link)
            except Exception:
                pass
        db.commit()
        
        # Import saved reports
        for report_data in data.get("saved_reports", []):
            try:
                existing = db.query(SavedReport).filter(SavedReport.id == report_data["id"]).first()
                if not existing:
                    report = SavedReport(
                        id=report_data["id"],
                        name=report_data["name"],
                        report_type=report_data.get("report_type"),
                        filters=report_data.get("filters")
                    )
                    db.add(report)
            except Exception:
                pass
        db.commit()
        
        print(f"[DataPersistence] Imported data: {len(data.get('categories', []))} categories, "
              f"{len(data.get('customers', []))} customers, {len(data.get('subscriptions', []))} subscriptions")
        
        return True
        
    except Exception as e:
        print(f"[DataPersistence] Error importing data: {e}")
        db.rollback()
        return False
    finally:
        _importing = False


def auto_save(db: Session):
    """Automatically save all data to file. Call this after any write operation."""
    global _importing
    
    if _importing:
        return
    
    try:
        data = export_all_data(db)
        save_data_to_file(data)
    except Exception as e:
        print(f"[DataPersistence] Auto-save error: {e}")


def check_and_restore_data(db: Session) -> bool:
    """
    Check if database is empty and restore from saved data if available.
    Checks environment variable first, then JSON file.
    Call this on application startup.
    Returns True if data was restored, False otherwise.
    """
    from app.models import Category
    
    try:
        # Check if database has data - only check categories to be safe
        has_categories = db.query(Category).first() is not None
        
        if has_categories:
            print("[DataPersistence] Database has existing data, skipping restore")
            return False
    except Exception as e:
        print(f"[DataPersistence] Error checking database: {e}")
        return False
    
    # Database is empty, try to restore from env var or file
    data = load_data()
    
    if data is None:
        print("[DataPersistence] No saved data found (checked env var and file)")
        return False
    
    # Check if there's actual data to restore
    if not data.get("categories") and not data.get("customers") and not data.get("subscriptions"):
        print("[DataPersistence] Saved data is empty, skipping restore")
        return False
    
    print("[DataPersistence] Database is empty, restoring from saved data...")
    return import_data_to_db(db, data)


def init_data_persistence():
    """Initialize data persistence on application startup."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        restored = check_and_restore_data(db)
        if restored:
            print("[DataPersistence] Data restoration complete")
        else:
            # If not restored, do an initial save of current data
            data = export_all_data(db)
            if data.get("categories") or data.get("customers") or data.get("subscriptions"):
                save_data_to_file(data)
                print("[DataPersistence] Initial data export complete")
    finally:
        db.close()
