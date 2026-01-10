"""Seed database with sample data."""
import sys
from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Category, Group, Customer, Subscription, User
from app.models.subscription import SubscriptionStatus, BillingCycle


def create_admin_user(db):
    """Create the default admin user if it doesn't exist."""
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("✓ Admin user already exists")
        return existing_admin
    
    print("Creating admin user...")
    admin = User(
        username="admin",
        email="admin@subtrack.local",
        is_admin=True,
        is_active=True
    )
    admin.set_password("admin")
    db.add(admin)
    db.commit()
    print("✓ Admin user created (username: admin, password: admin)")
    return admin


def seed_database():
    """Seed the database with sample data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create admin user first
        create_admin_user(db)
        
        print("Seeding data...")
        
        # Create categories
        print("Creating categories...")
        hosting = Category(
            name="Hosting & Infrastructure",
            description="Web hosting, cloud services, and infrastructure"
        )
        security = Category(
            name="Security & Antivirus",
            description="Security software and antivirus solutions"
        )
        productivity = Category(
            name="Productivity Tools",
            description="Business productivity and collaboration tools"
        )
        
        db.add_all([hosting, security, productivity])
        db.commit()
        
        # Create groups
        print("Creating groups...")
        vps_group = Group(
            category_id=hosting.id,
            name="VPS Servers",
            notes="Virtual private servers for various projects"
        )
        shared_hosting_group = Group(
            category_id=hosting.id,
            name="Shared Hosting",
            notes="Shared hosting accounts for client websites"
        )
        
        db.add_all([vps_group, shared_hosting_group])
        db.commit()
        
        # Create customers
        print("Creating customers...")
        customers_data = [
            {
                "name": "Acme Corp",
                "category_id": hosting.id,
                "group_id": vps_group.id,
                "email": "admin@acmecorp.com",
                "phone": "+1-555-0101",
                "tags": "enterprise,vip",
                "notes": "Main corporate client"
            },
            {
                "name": "TechStart Inc",
                "category_id": hosting.id,
                "group_id": vps_group.id,
                "email": "tech@techstart.io",
                "phone": "+1-555-0102",
                "tags": "startup,tech",
                "notes": "Startup client, growing fast"
            },
            {
                "name": "Digital Agency Pro",
                "category_id": hosting.id,
                "group_id": shared_hosting_group.id,
                "email": "hello@digitalagency.com",
                "phone": "+1-555-0103",
                "tags": "agency,creative",
                "notes": "Design and marketing agency"
            },
            {
                "name": "SecureNet Solutions",
                "category_id": security.id,
                "group_id": None,
                "email": "admin@securenet.com",
                "phone": "+1-555-0104",
                "tags": "security,enterprise",
                "notes": "Security-focused client"
            },
            {
                "name": "Global Enterprises",
                "category_id": productivity.id,
                "group_id": None,
                "email": "it@globalent.com",
                "phone": "+1-555-0105",
                "tags": "enterprise,global",
                "notes": "Large multinational corporation"
            },
            {
                "name": "Acme Digital",
                "category_id": security.id,
                "group_id": None,
                "email": "security@acmecorp.com",
                "phone": "+1-555-0101",
                "tags": "enterprise,vip",
                "notes": "Security division of Acme Corp"
            }
        ]
        
        customers = []
        for data in customers_data:
            customer = Customer(**data)
            db.add(customer)
            customers.append(customer)
        
        db.commit()
        
        # Create subscriptions
        print("Creating subscriptions...")
        today = date.today()
        
        subscriptions_data = [
            # Hosting subscriptions
            {
                "customer_id": customers[0].id,
                "category_id": hosting.id,
                "vendor_name": "DigitalOcean",
                "plan_name": "Professional Droplet",
                "cost": 120.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=180),
                "next_renewal_date": today + timedelta(days=5),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "Main production server"
            },
            {
                "customer_id": customers[1].id,
                "category_id": hosting.id,
                "vendor_name": "AWS",
                "plan_name": "EC2 t3.large",
                "cost": 250.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=90),
                "next_renewal_date": today + timedelta(days=15),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "Application server"
            },
            {
                "customer_id": customers[2].id,
                "category_id": hosting.id,
                "vendor_name": "SiteGround",
                "plan_name": "GrowBig Plan",
                "cost": 14.99,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=365),
                "next_renewal_date": today + timedelta(days=25),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "Client website hosting"
            },
            {
                "customer_id": customers[0].id,
                "category_id": hosting.id,
                "vendor_name": "Cloudflare",
                "plan_name": "Pro Plan",
                "cost": 20.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=200),
                "next_renewal_date": today - timedelta(days=2),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "CDN and security"
            },
            # Security subscriptions
            {
                "customer_id": customers[3].id,
                "category_id": security.id,
                "vendor_name": "ESET",
                "plan_name": "Endpoint Protection Standard",
                "cost": 299.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.YEARLY,
                "start_date": today - timedelta(days=300),
                "next_renewal_date": today + timedelta(days=45),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "50 user licenses"
            },
            {
                "customer_id": customers[5].id,
                "category_id": security.id,
                "vendor_name": "ESET",
                "plan_name": "Endpoint Protection Advanced",
                "cost": 499.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.YEARLY,
                "start_date": today - timedelta(days=310),
                "next_renewal_date": today + timedelta(days=35),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "100 user licenses for Acme Corp security"
            },
            {
                "customer_id": customers[3].id,
                "category_id": security.id,
                "vendor_name": "Malwarebytes",
                "plan_name": "Business Plan",
                "cost": 79.99,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=150),
                "next_renewal_date": today + timedelta(days=8),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "Additional malware protection"
            },
            # Productivity subscriptions
            {
                "customer_id": customers[4].id,
                "category_id": productivity.id,
                "vendor_name": "Microsoft 365",
                "plan_name": "Business Premium",
                "cost": 1200.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=400),
                "next_renewal_date": today + timedelta(days=12),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "100 user licenses"
            },
            {
                "customer_id": customers[4].id,
                "category_id": productivity.id,
                "vendor_name": "Slack",
                "plan_name": "Business+ Plan",
                "cost": 450.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=250),
                "next_renewal_date": today + timedelta(days=18),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "Team communication"
            },
            {
                "customer_id": customers[1].id,
                "category_id": productivity.id,
                "vendor_name": "Notion",
                "plan_name": "Team Plan",
                "cost": 80.00,
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "start_date": today - timedelta(days=60),
                "next_renewal_date": today + timedelta(days=22),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "Project management and documentation"
            },
            # Overdue subscription
            {
                "customer_id": customers[2].id,
                "category_id": hosting.id,
                "vendor_name": "Namecheap",
                "plan_name": "Domain Registration",
                "cost": 12.98,
                "currency": "USD",
                "billing_cycle": BillingCycle.YEARLY,
                "start_date": today - timedelta(days=380),
                "next_renewal_date": today - timedelta(days=15),
                "status": SubscriptionStatus.ACTIVE,
                "notes": "Domain renewal overdue!"
            }
        ]
        
        for data in subscriptions_data:
            subscription = Subscription(**data)
            db.add(subscription)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - {len([hosting, security, productivity])} categories")
        print(f"   - {len([vps_group, shared_hosting_group])} groups")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(subscriptions_data)} subscriptions")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
