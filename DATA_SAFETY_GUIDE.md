# Data Safety Guide

## Your Data is Safe! 🔒

The code changes made by AI assistants **do not affect your actual database data**. Here's why:

---

## What Gets Changed vs What Doesn't

### ✅ Code Changes (Version Controlled)
These are tracked by Git and pushed to your repository:
- Python files (.py)
- HTML templates
- JavaScript files
- CSS stylesheets
- Configuration files

### ❌ Data Files (NOT Version Controlled)
These are in your `.gitignore` and **never** pushed to the repository:
- `*.db` - Your SQLite database
- `*.db-journal` - Database journal files
- `.env` - Environment variables (passwords, API keys)
- `__pycache__/` - Python cache files

---

## How to Verify Your Data Safety

### 1. Check Your .gitignore
Your `.gitignore` already has these protective entries:
```
*.db
*.db-journal
.env
```

### 2. Check What Git Tracks
Run this command to see what files Git is tracking:
```bash
git status
```

Your database files should **never** appear here!

### 3. View Tracked Files
```bash
git ls-files
```

This shows all files in the repository. Database files should not be listed.

---

## Database Migration Safety

When you run migrations (`alembic upgrade head`):
- ✅ Schema changes (adds columns, tables)
- ✅ Preserves all existing data
- ❌ Does NOT delete or modify data

Example: Adding a `country` field to customers:
- All existing customers remain unchanged
- New `country` column is added with `NULL` values
- You can fill in country data later

---

## Best Practices for Data Safety

### 1. Always Backup Before Major Changes
```bash
# Create a backup
cp subtrack.db subtrack.db.backup

# Or with date
cp subtrack.db subtrack.db.backup.$(date +%Y%m%d)
```

### 2. Test Migrations in Development First
```bash
# On your local machine, test the migration
alembic upgrade head

# If successful, then deploy to production
```

### 3. Use Environment Variables
Never commit sensitive data:
```bash
# .env (ignored by Git)
DATABASE_URL=sqlite:///./subtrack.db
SECRET_KEY=your-secret-key
```

### 4. Regular Backups
Set up automatic backups:
- Daily database backups
- Keep backups for 30 days
- Test restore procedures

---

## What Happens When You Git Pull/Push

### Git Pull (Getting Changes)
```bash
git pull origin main
```
**What Changes:**
- Code files update
- Templates update
- Migrations are added

**What Doesn't Change:**
- Your database data
- Your `.env` settings
- User uploads

### Git Push (Sending Changes)
```bash
git push origin main
```
**What Gets Pushed:**
- Code changes you made
- New templates/styles
- Configuration changes

**What Doesn't Get Pushed:**
- Database files (*.db)
- Environment variables (.env)
- Any file in `.gitignore`

---

## Recovery Procedures

### If You Accidentally Commit Your Database

1. Remove from Git history:
```bash
git rm --cached subtrack.db
git commit -m "Remove database from tracking"
```

2. Ensure .gitignore has `*.db`

3. Push changes:
```bash
git push origin main
```

### If You Lose Data

1. Restore from backup:
```bash
cp subtrack.db.backup subtrack.db
```

2. Or rollback migration:
```bash
alembic downgrade -1
```

---

## File Location Reference

### Development (Local)
```
your-project/
├── subtrack.db          # Your local database (NOT in Git)
├── .env                 # Your local settings (NOT in Git)
├── app/                 # Code (IN Git)
├── static/              # Static files (IN Git)
└── alembic/             # Migrations (IN Git)
```

### Production (Railway/Heroku)
```
Uses PostgreSQL database
- Database hosted separately
- Environment variables in platform settings
- Code deployed from Git
- Data never in Git repository
```

---

## Quick Checklist Before Any Update

- [ ] Backup your database
- [ ] Verify `.gitignore` includes `*.db`
- [ ] Test changes locally first
- [ ] Run `git status` to verify what's being committed
- [ ] Only commit code changes, never data files

---

## Summary

✅ **Safe to Push:** Code, templates, CSS, JS, migrations
❌ **Never Push:** Database files, .env, API keys, passwords

Your `.gitignore` is properly configured, so your data is protected! 🛡️
