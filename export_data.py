"""Export all data from the database to a JSON file."""
import json
from datetime import date, datetime
from app.database import SessionLocal
from app.models import Category, Group, Customer, Subscription, User

def datetime_handler(obj):
    """JSON serializer for datetime objects."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def export_data():
    """Export all data to JSON file."""
    db = SessionLocal()
    
    try:
        data = {
            "categories": [],
            "groups": [],
            "customers": [],
            "subscriptions": [],
            "users": []
        }
        
        # Export categories
        print("Exporting categories...")
        for cat in db.query(Category).all():
            data["categories"].append({
                "id": cat.id,
                "name": cat.name,
                "description": cat.description
            })
        
        # Export groups
        print("Exporting groups...")
        for group in db.query(Group).all():
            data["groups"].append({
                "id": group.id,
                "category_id": group.category_id,
                "name": group.name,
                "notes": group.notes
            })
        
        # Export customers
        print("Exporting customers...")
        for customer in db.query(Customer).all():
            data["customers"].append({
                "id": customer.id,
                "category_id": customer.category_id,
                "group_id": customer.group_id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "tags": customer.tags,
                "notes": customer.notes
            })
        
        # Export subscriptions
        print("Exporting subscriptions...")
        for sub in db.query(Subscription).all():
            data["subscriptions"].append({
                "id": sub.id,
                "customer_id": sub.customer_id,
                "category_id": sub.category_id,
                "vendor_name": sub.vendor_name,
                "plan_name": sub.plan_name,
                "cost": sub.cost,
                "currency": sub.currency,
                "billing_cycle": sub.billing_cycle.value,
                "start_date": sub.start_date.isoformat(),
                "next_renewal_date": sub.next_renewal_date.isoformat(),
                "status": sub.status.value,
                "notes": sub.notes
            })
        
        # Export users (excluding passwords for security)
        print("Exporting users (without passwords)...")
        for user in db.query(User).all():
            data["users"].append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        # Save to file
        filename = "subtrack_data_export.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=datetime_handler)
        
        print(f"\n✅ Data exported successfully to {filename}")
        print(f"   Categories: {len(data['categories'])}")
        print(f"   Groups: {len(data['groups'])}")
        print(f"   Customers: {len(data['customers'])}")
        print(f"   Subscriptions: {len(data['subscriptions'])}")
        print(f"   Users: {len(data['users'])}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    export_data()
