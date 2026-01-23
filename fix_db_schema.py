from sqlalchemy import text
from app.database import engine

def fix_schema():
    print("Fixing database schema...")
    with engine.connect() as conn:
        try:
            # Check if user_id column exists
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='check_categories' AND column_name='user_id'"
            )).fetchone()
            
            if not result:
                print("Adding user_id column to check_categories...")
                conn.execute(text("ALTER TABLE check_categories ADD COLUMN user_id INTEGER"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column check_categories.user_id already exists.")
                
        except Exception as e:
            print(f"Error executing schema fix: {str(e)}")
            # Fallback for SQLite if the above Postgres-specific query fails
            if "no such table" in str(e).lower() or "syntax" in str(e).lower():
                 print("Attempting SQLite fallback...")
                 try:
                     conn.execute(text("ALTER TABLE check_categories ADD COLUMN user_id INTEGER"))
                     conn.commit()
                     print("SQLite column added.")
                 except Exception as inner_e:
                     print(f"SQLite fallback failed: {inner_e}")

if __name__ == "__main__":
    fix_schema()
