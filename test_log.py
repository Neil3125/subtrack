import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.routers.log_check_routes import LogGenerateRequest
from app.database import SessionLocal
from app.models.user import User

client = TestClient(app)

def test():
    db = SessionLocal()
    # Get any user or create a dummy one
    user = db.query(User).first()
    if not user:
        user = User(email="test@test.com", username="testuser", hashed_password="pw")
        db.add(user)
        db.commit()
    
    # We need to test the generate API itself. 
    # Since it's protected by AuthMiddleware and get_current_user, we can just call the endpoint logic directly.
    from app.routers.log_check_routes import generate_log
    
    req = LogGenerateRequest(check_type="service", mode="automatic", hours=0, minutes=30)
    
    import asyncio
    try:
        res = asyncio.run(generate_log(request=req, db=db, user=user))
        print("API Response:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

test()
