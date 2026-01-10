"""Initialize authentication - creates users table and admin user."""
from app.database import SessionLocal, engine, Base
from app.models.user import User

def init_auth():
    """Create users table and admin user."""
    print("Initializing authentication...")
    
    # Create all tables (including users)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
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
        
        print("=" * 50)
        print("✓ Authentication initialized successfully!")
        print("=" * 50)
        print("Default admin credentials:")
        print("  Username: admin")
        print("  Password: admin")
        print("=" * 50)
        print("⚠️  Please change the password after first login!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_auth()
