"""Database backup utility for SubTrack."""
import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_database():
    """Create a timestamped backup of the database."""
    db_file = "subtrack.db"
    
    if not os.path.exists(db_file):
        print(f"❌ Database file '{db_file}' not found!")
        return False
    
    # Create backups directory if it doesn't exist
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"subtrack_backup_{timestamp}.db"
    
    try:
        # Copy database file
        shutil.copy2(db_file, backup_file)
        file_size = os.path.getsize(backup_file)
        print(f"✅ Database backed up successfully!")
        print(f"   📁 Location: {backup_file}")
        print(f"   📊 Size: {file_size:,} bytes")
        
        # Clean old backups (keep last 10)
        cleanup_old_backups(backup_dir, keep=10)
        
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False


def cleanup_old_backups(backup_dir: Path, keep: int = 10):
    """Remove old backups, keeping only the most recent ones."""
    backup_files = sorted(
        backup_dir.glob("subtrack_backup_*.db"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if len(backup_files) > keep:
        for old_backup in backup_files[keep:]:
            try:
                old_backup.unlink()
                print(f"   🗑️  Removed old backup: {old_backup.name}")
            except Exception as e:
                print(f"   ⚠️  Could not remove {old_backup.name}: {e}")


def restore_database(backup_file: str):
    """Restore database from a backup file."""
    db_file = "subtrack.db"
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file '{backup_file}' not found!")
        return False
    
    try:
        # Create a backup of current database before restoring
        if os.path.exists(db_file):
            current_backup = f"{db_file}.before_restore"
            shutil.copy2(db_file, current_backup)
            print(f"   💾 Current database backed up to: {current_backup}")
        
        # Restore from backup
        shutil.copy2(backup_file, db_file)
        print(f"✅ Database restored successfully from {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False


def list_backups():
    """List all available backups."""
    backup_dir = Path("backups")
    
    if not backup_dir.exists():
        print("No backups directory found.")
        return
    
    backup_files = sorted(
        backup_dir.glob("subtrack_backup_*.db"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if not backup_files:
        print("No backups found.")
        return
    
    print(f"\n📦 Available Backups ({len(backup_files)} total):\n")
    for i, backup in enumerate(backup_files, 1):
        size = backup.stat().st_size
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{i}. {backup.name}")
        print(f"   📅 {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📊 {size:,} bytes\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "backup":
            backup_database()
        elif command == "list":
            list_backups()
        elif command == "restore" and len(sys.argv) > 2:
            restore_database(sys.argv[2])
        else:
            print("Usage:")
            print("  python backup_database.py backup              - Create a backup")
            print("  python backup_database.py list                - List all backups")
            print("  python backup_database.py restore <filename>  - Restore from backup")
    else:
        # Default: create backup
        backup_database()
