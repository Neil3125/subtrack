import sys
from app.database import SessionLocal
from app.models import User
from app.security import get_password_hash

try:
    db = SessionLocal()
    if not db.query(User).filter(User.username == 'admin').first():
        user = User(username='admin', email='admin@test.com', hashed_password=get_password_hash('admin'))
        db.add(user)
        db.commit()
        print("Admin user created.")
    else:
        print("Admin already exists.")
except Exception as e:
    print(f"Error: {e}")
