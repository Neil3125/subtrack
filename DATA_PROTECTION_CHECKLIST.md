# Data Protection Checklist ✅

## Before Every Git Push

Run this checklist to ensure your data is safe:

### 1. Check What You're Committing
```bash
git status
```
**Expected**: Should NOT see any `.db` files listed

### 2. Create a Backup (Recommended)
```bash
python backup_database.py
```
**Result**: Creates a timestamped backup in `backups/` folder

### 3. Verify .db Files Are Ignored
```bash
git check-ignore *.db
```
**Expected**: Should output `subtrack.db` (meaning it's ignored)

### 4. List Tracked Files
```bash
git ls-files | findstr /i ".db"
```
**Expected**: No output (no .db files tracked)

---

## Database Location

Your data lives in: `subtrack.db`

This file is:
- ✅ In your `.gitignore`
- ✅ Never pushed to GitHub
- ✅ Stays on your local machine
- ✅ Protected by backups

---

## Why You Might See "Data Loss"

### Common Scenarios:

1. **Working on Multiple Machines**
   - Each machine has its own `subtrack.db`
   - Changes on Machine A won't appear on Machine B
   - **Solution**: Use database backup/restore to sync

2. **Fresh Git Clone**
   - Cloning creates a new empty database
   - Your data is still on the original machine
   - **Solution**: Copy `subtrack.db` from old location

3. **Running Migrations**
   - Migration errors might corrupt data
   - **Solution**: Always backup before migrations

4. **Development vs Production**
   - Local database ≠ Production database
   - They are completely separate
   - **Solution**: Export/import data or use separate environments

---

## Quick Commands

### Backup Your Database
```bash
python backup_database.py backup
```

### List All Backups
```bash
python backup_database.py list
```

### Restore from Backup
```bash
python backup_database.py restore backups/subtrack_backup_YYYYMMDD_HHMMSS.db
```

### Check If Database Is Tracked by Git
```bash
git ls-files | findstr /i "subtrack.db"
```
If this returns nothing, you're safe! ✅

### Remove Database from Git (If Accidentally Added)
```bash
git rm --cached subtrack.db
git commit -m "Remove database from tracking"
git push
```

---

## Best Practices

1. **Backup Before Every Major Change**
   ```bash
   python backup_database.py
   ```

2. **Check Git Status Before Push**
   ```bash
   git status
   # Verify no .db files listed
   ```

3. **Use Environment Variables for Sensitive Data**
   - Never commit `.env` file
   - Store API keys, passwords in `.env`

4. **Keep Local and Remote Separate**
   - Local database = your development data
   - Remote/Production = live production data
   - Don't mix them!

---

## Emergency Recovery

### If You Lost Data

1. **Check backups folder:**
   ```bash
   python backup_database.py list
   ```

2. **Restore most recent backup:**
   ```bash
   python backup_database.py restore backups/[latest_backup].db
   ```

3. **If no backups exist:**
   - Check other machines
   - Check recycle bin
   - Look for `.db-journal` files (might contain recent changes)

---

## Summary

✅ **Your .gitignore is correct** - `*.db` is excluded
✅ **Backup script created** - Run before changes
✅ **Database is local** - Never pushed to GitHub

**When you push code:**
- ✅ Code changes → GitHub
- ❌ Database data → Stays local
- ✅ Backups → Stays local (in `backups/` folder)

Your data is safe! 🔒
