"""Seed the database with sample data for testing and demonstration."""
from datetime import date, timedelta
from app.database import SessionLocal
from app.models import Category, Group, Customer, Subscription
from app.models.subscription import BillingCycle, SubscriptionStatus

def seed_database():
    """Populate the database with sample data."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Category).count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        print("Seeding database with sample data...")
        
        # Create Categories
        categories = [
            Category(name="Security & Antivirus", description="Security software, antivirus, and endpoint protection"),
            Category(name="Business Software", description="Accounting, CRM, and business management tools"),
            Category(name="Cloud & Infrastructure", description="Hosting, cloud services, and infrastructure"),
            Category(name="Productivity & Collaboration", description="Office suites, email, and team collaboration"),
            Category(name="Development Tools", description="Developer platforms and version control"),
            Category(name="Marketing & Analytics", description="Marketing automation and analytics platforms")
        ]
        
        for category in categories:
            db.add(category)
        db.commit()
        print(f"Created {len(categories)} categories")
        
        # Create Groups
        groups = [
            Group(category_id=1, name="IT Security Team", notes="Manages all security subscriptions"),
            Group(category_id=2, name="Finance Department", notes="Accounting and financial software"),
            Group(category_id=4, name="All Staff", notes="Company-wide productivity tools"),
            Group(category_id=5, name="Development Team", notes="Developer tools and services")
        ]
        
        for group in groups:
            db.add(group)
        db.commit()
        print(f"Created {len(groups)} groups")
        
        # Create Customers
        customers = [
            Customer(
                category_id=1,
                group_id=1,
                name="TechCorp Industries",
                email="security@techcorp.com",
                phone="+1-555-0100",
                tags="enterprise,security-focused",
                notes="Large enterprise with 200+ employees requiring comprehensive security"
            ),
            Customer(
                category_id=2,
                group_id=2,
                name="Green Valley Consulting",
                email="admin@greenvalley.com",
                phone="+1-555-0101",
                tags="consulting,small-business",
                notes="15-person consulting firm specializing in business strategy"
            ),
            Customer(
                category_id=4,
                group_id=3,
                name="Digital Marketing Pro",
                email="info@digitalmarketingpro.com",
                phone="+1-555-0102",
                tags="marketing,agency",
                notes="Marketing agency with 30 employees"
            ),
            Customer(
                category_id=5,
                group_id=4,
                name="CloudDev Solutions",
                email="devops@clouddev.io",
                phone="+1-555-0103",
                tags="software,development",
                notes="Software development company with 50 developers"
            ),
            Customer(
                category_id=2,
                name="Retail Plus Stores",
                email="corporate@retailplus.com",
                phone="+1-555-0104",
                tags="retail,multi-location",
                notes="Retail chain with 8 locations"
            ),
            Customer(
                category_id=1,
                group_id=1,
                name="SecureFinance Corp",
                email="it@securefinance.com",
                phone="+1-555-0105",
                tags="finance,high-security",
                notes="Financial services firm with strict compliance requirements"
            )
        ]
        
        for customer in customers:
            db.add(customer)
        db.commit()
        print(f"Created {len(customers)} customers")
        
        # Create Subscriptions
        today = date.today()
        subscriptions = [
            # TechCorp Industries - Security focused
            Subscription(
                customer_id=1,
                category_id=1,
                vendor_name="ESET",
                plan_name="ESET PROTECT Advanced",
                cost=1899.00,
                currency="USD",
                billing_cycle=BillingCycle.YEARLY,
                start_date=today - timedelta(days=120),
                next_renewal_date=today + timedelta(days=245),
                status=SubscriptionStatus.ACTIVE,
                notes="200 device licenses - comprehensive endpoint protection with cloud sandboxing"
            ),
            Subscription(
                customer_id=1,
                category_id=1,
                vendor_name="Cloudflare",
                plan_name="Business Plan",
                cost=200.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=180),
                next_renewal_date=today + timedelta(days=20),
                status=SubscriptionStatus.ACTIVE,
                notes="DDoS protection and web application firewall"
            ),
            Subscription(
                customer_id=1,
                category_id=4,
                vendor_name="Microsoft",
                plan_name="Microsoft 365 E3",
                cost=36.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=400),
                next_renewal_date=today + timedelta(days=10),
                status=SubscriptionStatus.ACTIVE,
                notes="Per user - 200 licenses for full office suite and enterprise features"
            ),
            
            # Green Valley Consulting - Business tools
            Subscription(
                customer_id=2,
                category_id=2,
                vendor_name="Intuit",
                plan_name="QuickBooks Online Advanced",
                cost=180.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=500),
                next_renewal_date=today + timedelta(days=8),
                status=SubscriptionStatus.ACTIVE,
                notes="Advanced accounting features with dedicated support"
            ),
            Subscription(
                customer_id=2,
                category_id=2,
                vendor_name="Salesforce",
                plan_name="Professional Edition",
                cost=75.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=200),
                next_renewal_date=today + timedelta(days=15),
                status=SubscriptionStatus.ACTIVE,
                notes="CRM for client management - 15 user licenses"
            ),
            Subscription(
                customer_id=2,
                category_id=1,
                vendor_name="Malwarebytes",
                plan_name="Endpoint Protection",
                cost=479.88,
                currency="USD",
                billing_cycle=BillingCycle.YEARLY,
                start_date=today - timedelta(days=90),
                next_renewal_date=today + timedelta(days=275),
                status=SubscriptionStatus.ACTIVE,
                notes="15 devices - anti-malware protection"
            ),
            
            # Digital Marketing Pro
            Subscription(
                customer_id=3,
                category_id=6,
                vendor_name="Google",
                plan_name="Google Workspace Business Standard",
                cost=12.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=600),
                next_renewal_date=today + timedelta(days=5),
                status=SubscriptionStatus.ACTIVE,
                notes="Per user - 30 licenses for email and productivity"
            ),
            Subscription(
                customer_id=3,
                category_id=6,
                vendor_name="HubSpot",
                plan_name="Marketing Hub Professional",
                cost=890.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=250),
                next_renewal_date=today + timedelta(days=12),
                status=SubscriptionStatus.ACTIVE,
                notes="Complete marketing automation platform"
            ),
            Subscription(
                customer_id=3,
                category_id=6,
                vendor_name="Adobe",
                plan_name="Creative Cloud All Apps",
                cost=54.99,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=150),
                next_renewal_date=today + timedelta(days=18),
                status=SubscriptionStatus.ACTIVE,
                notes="Per user - 20 licenses for design team"
            ),
            
            # CloudDev Solutions - Developer tools
            Subscription(
                customer_id=4,
                category_id=5,
                vendor_name="GitHub",
                plan_name="Enterprise Cloud",
                cost=21.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=365),
                next_renewal_date=today + timedelta(days=25),
                status=SubscriptionStatus.ACTIVE,
                notes="Per user - 50 developer seats with advanced security"
            ),
            Subscription(
                customer_id=4,
                category_id=3,
                vendor_name="Amazon Web Services",
                plan_name="Business Support",
                cost=2500.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=800),
                next_renewal_date=today + timedelta(days=7),
                status=SubscriptionStatus.ACTIVE,
                notes="Cloud infrastructure and 24/7 technical support"
            ),
            Subscription(
                customer_id=4,
                category_id=5,
                vendor_name="JetBrains",
                plan_name="All Products Pack",
                cost=649.00,
                currency="USD",
                billing_cycle=BillingCycle.YEARLY,
                start_date=today - timedelta(days=100),
                next_renewal_date=today + timedelta(days=265),
                status=SubscriptionStatus.ACTIVE,
                notes="50 licenses - IDE suite for development team"
            ),
            
            # Retail Plus Stores
            Subscription(
                customer_id=5,
                category_id=2,
                vendor_name="Square",
                plan_name="Square for Retail Plus",
                cost=60.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=300),
                next_renewal_date=today + timedelta(days=22),
                status=SubscriptionStatus.ACTIVE,
                notes="POS system for 8 retail locations"
            ),
            Subscription(
                customer_id=5,
                category_id=2,
                vendor_name="Intuit",
                plan_name="QuickBooks Online Plus",
                cost=90.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=450),
                next_renewal_date=today + timedelta(days=14),
                status=SubscriptionStatus.ACTIVE,
                notes="Multi-store accounting and inventory management"
            ),
            Subscription(
                customer_id=5,
                category_id=4,
                vendor_name="Slack",
                plan_name="Pro Plan",
                cost=7.25,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=220),
                next_renewal_date=today + timedelta(days=9),
                status=SubscriptionStatus.ACTIVE,
                notes="Per user - 40 licenses for team communication across locations"
            ),
            
            # SecureFinance Corp - High security
            Subscription(
                customer_id=6,
                category_id=1,
                vendor_name="ESET",
                plan_name="ESET PROTECT Complete",
                cost=3299.00,
                currency="USD",
                billing_cycle=BillingCycle.YEARLY,
                start_date=today - timedelta(days=200),
                next_renewal_date=today + timedelta(days=165),
                status=SubscriptionStatus.ACTIVE,
                notes="150 devices - full encryption and multi-factor authentication"
            ),
            Subscription(
                customer_id=6,
                category_id=1,
                vendor_name="Cisco",
                plan_name="Cisco Umbrella",
                cost=399.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=280),
                next_renewal_date=today + timedelta(days=11),
                status=SubscriptionStatus.ACTIVE,
                notes="Cloud-delivered security service - DNS filtering and threat intelligence"
            ),
            Subscription(
                customer_id=6,
                category_id=2,
                vendor_name="Bloomberg",
                plan_name="Bloomberg Terminal",
                cost=2000.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=900),
                next_renewal_date=today + timedelta(days=16),
                status=SubscriptionStatus.ACTIVE,
                notes="5 terminals for financial data and analytics"
            ),
            Subscription(
                customer_id=6,
                category_id=3,
                vendor_name="Microsoft Azure",
                plan_name="Enterprise Agreement",
                cost=5000.00,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                start_date=today - timedelta(days=700),
                next_renewal_date=today + timedelta(days=28),
                status=SubscriptionStatus.ACTIVE,
                notes="Cloud infrastructure with compliance and security features"
            )
        ]
        
        for subscription in subscriptions:
            db.add(subscription)
        db.commit()
        print(f"Created {len(subscriptions)} subscriptions")
        
        print("\n✅ Database seeded successfully!")
        print(f"   Categories: {len(categories)}")
        print(f"   Groups: {len(groups)}")
        print(f"   Customers: {len(customers)}")
        print(f"   Subscriptions: {len(subscriptions)}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
