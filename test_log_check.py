import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.log_entry import LogEntry
from app.models.user import User

async def run_test():
    db = SessionLocal()
    
    user = db.query(User).first()
    if not user:
        print("No user found")
        return
        
    print(f"Testing with User: {user.email}")
    
    # 1. Create a log
    new_log = LogEntry(
        date_str="03/06/2026",
        start_time="10:00 a.m",
        end_time="10:30 a.m",
        duration_minutes=30,
        check_type="service",
        message="Test Verification Log",
        full_entry="[Test] Log entry",
        user_id=user.id
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    print(f"Created Log ID: {new_log.id}")
    
    # 2. Select the log back
    logs = db.query(LogEntry).filter(LogEntry.user_id == user.id).all()
    print(f"User has {len(logs)} logs.")
    assert any(l.id == new_log.id for l in logs), "Log not found for user"
    
    # 3. Update the log
    new_log.full_entry = "[Test] Log entry [EDITED]"
    db.commit()
    
    # Verify update
    updated_log = db.query(LogEntry).filter(LogEntry.id == new_log.id).first()
    print(f"Updated full_entry: {updated_log.full_entry}")
    assert "[EDITED]" in updated_log.full_entry
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    asyncio.run(run_test())
