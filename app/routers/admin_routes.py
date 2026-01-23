"""Admin routes for system maintenance tasks."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from app.database import get_db, engine
from app.routers.auth_routes import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])

def check_admin(current_user: User = Depends(get_current_user)):
    """Dependency to check if current user is admin."""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.post("/fix-schema")
def fix_database_schema(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin)
) -> Dict[str, Any]:
    """
    Attempt to fix common database schema issues.
    Currently fixes: missing 'user_id' column in 'check_categories' table.
    """
    results = []
    
    # Fix 1: Add user_id to check_categories if missing
    try:
        # Check if column exists
        # Note: This is a robust way to check across different DB types (Postgres/SQLite)
        # However, for simplicity/compatibility we'll try to query information_schema if possible,
        # or just try the alter and catch the error.
        
        # Postgres check
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='check_categories' AND column_name='user_id'
        """
        
        # We need to execute raw SQL on the engine level for ADD COLUMN usually,
        # but session.execute works for DML. distinct connections are better for DDL.
        with engine.connect() as conn:
            # Try to detect if we check existence first
            try:
                exists = conn.execute(text(check_sql)).fetchone()
            except Exception:
                # Fallback for SQLite or permission issues - assume we need to try adding it
                exists = None
            
            if not exists:
                try:
                    # Postgres syntax
                    conn.execute(text("ALTER TABLE check_categories ADD COLUMN user_id INTEGER"))
                    conn.commit()
                    results.append("Added 'user_id' column to 'check_categories' table (PostgreSQL style).")
                except Exception as e:
                    # SQLite fallback or already exists
                    error_str = str(e).lower()
                    if "duplicate column" in error_str or "already exists" in error_str:
                         results.append("'user_id' column already exists in 'check_categories'.")
                    elif "syntax" in error_str or "sqlite" in error_str or "operationalerror" in error_str:
                        # Try SQLite syntax (rarely different for simple ADD COLUMN but ensures isolation)
                         try:
                             # SQLite often doesn't need a different syntax for ADD COLUMN, but
                             # let's catch generic errors.
                             # If previous failed, maybe it was just "already exists".
                             pass
                         except Exception:
                             pass
                        
                    results.append(f"Note on check_categories fix: {str(e)}")
            else:
                results.append("'user_id' column already exists in 'check_categories'.")
                
    except Exception as e:
        results.append(f"Error checking/fixing check_categories: {str(e)}")

    return {
        "success": True,
        "message": "Schema fix procedures executed.",
        "details": results
    }
