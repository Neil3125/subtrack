import asyncio
from app.main import app
from app.database import SessionLocal
from app.models.user import User

def create_test_user():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            username="test@example.com",
            is_active=True
        )
        user.set_password("password")
        db.add(user)
    else:
        user.set_password("password")
        user.is_active = True
    db.commit()
    print("Test user ready!")

create_test_user()
