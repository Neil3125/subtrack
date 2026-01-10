"""Import data from JSON file to the database."""
import json
from datetime import datetime, date
from app.database import SessionLocal
from app.models import Category, Group, Customer, Subscription
from app.models.subscription import BillingCycle, SubscriptionStatus

def import_data(filename="subtrack_data_export.json"):
    """Import data from JSON file."""
    db = SessionLocal()
    
    try:
        # Load data from file
        print(f"Loading data from {filename}...")
        with open(filename, "r") as f:
            data = json.load(f)
        
        # Clear existing data (except users)
        print("Clearing existing data...")
        db.query(Subscription).delete()
        db.query(Customer).delete()
        db.query(Group).delete()
        db.query(Category).delete()
        db.commit()
        
        # Import categories
        print(f"Importing {len(data['categories'])} categories...")
        for cat_data in data["categories"]:
            cat = Category(
                id=cat_data["id"],
                name=cat_data["name"],
                description=cat_data["description"]
            )
            db.add(cat)
        db.commit()
        
        # Import groups
        print(f"Importing {len(data['groups'])} groups...")
        for group_data in data["groups"]:
            group = Group(
                id=group_data["id"],
                category_id=group_data["category_id"],
                name=group_data["name"],
                notes=group_data["notes"]
            )
            db.add(group)
        db.commit()
        
        # Import customers
        print(f"Importing {len(data['customers'])} customers...")
        for customer_data in data["customers"]:
            customer = Customer(
                id=customer_data["id"],
                category_id=customer_data["category_id"],
                group_id=customer_data["group_id"],
                name=customer_data["name"],
                email=customer_data["email"],
                phone=customer_data["phone"],
                tags=customer_data["tags"],
                notes=customer_data["notes"]
            )
            db.add(customer)
        db.commit()
        
        # Import subscriptions
        print(f"Importing {len(data['subscriptions'])} subscriptions...")
        for sub_data in data["subscriptions"]:
            sub = Subscription(
                id=sub_data["id"],
                customer_id=sub_data["customer_id"],
                category_id=sub_data["category_id"],
                vendor_name=sub_data["vendor_name"],
                plan_name=sub_data["plan_name"],
                cost=sub_data["cost"],
                currency=sub_data["currency"],
                billing_cycle=BillingCycle(sub_data["billing_cycle"]),
                start_date=datetime.fromisoformat(sub_data["start_date"]).date(),
                next_renewal_date=datetime.fromisoformat(sub_data["next_renewal_date"]).date(),
                status=SubscriptionStatus(sub_data["status"]),
                notes=sub_data["notes"]
            )
            db.add(sub)
        db.commit()
        
        print("\n✅ Data imported successfully!")
        print(f"   Categories: {len(data['categories'])}")
        print(f"   Groups: {len(data['groups'])}")
        print(f"   Customers: {len(data['customers'])}")
        print(f"   Subscriptions: {len(data['subscriptions'])}")
        print("\n⚠️  Note: User passwords were not imported for security reasons.")
        print("   Use the default admin/admin credentials or create new users.")
        
    except Exception as e:
        print(f"❌ Error importing data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "subtrack_data_export.json"
    import_data(filename)
