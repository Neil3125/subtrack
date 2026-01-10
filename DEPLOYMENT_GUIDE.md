# SubTrack Deployment Guide

## Deploying to Railway (Recommended for Full-Stack Apps)

Railway is perfect for your SubTrack app because it supports both Python backends and database persistence.

### Prerequisites
- GitHub account (free)
- Railway account (free tier available)
- Your SubTrack code on GitHub

---

## Phase 1: Prepare Your Code

### 1.1 Update Configuration for Production

Your app needs to work with environment variables. Check your `app/config.py`:

```python
# Should use environment variables:
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./subtrack.db")
```

### 1.2 Verify Procfile Exists

The `Procfile` tells Railway how to start your app:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

This file should be in your project root.

### 1.3 Check requirements.txt

All dependencies should be listed with versions. Run locally:

```bash
pip freeze > requirements.txt
```

---

## Phase 2: Push Code to GitHub

### 2.1 Create GitHub Repository

1. Go to https://github.com/new
2. Create repository named `subtrack`
3. **Do NOT** initialize with README (you have one already)

### 2.2 Push Your Code

```powershell
# Navigate to your project
cd C:\path\to\subtrack

# Initialize git if not already done
git init

# Add everything
git add .

# Commit
git commit -m "Initial SubTrack commit"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/subtrack.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Verify:** Visit `https://github.com/YOUR_USERNAME/subtrack` to confirm code is there.

---

## Phase 3: Deploy to Railway

### 3.1 Sign Up on Railway

1. Go to https://railway.app
2. Click "Start with GitHub"
3. Authorize Railway to access your GitHub

### 3.2 Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Find and select `subtrack`
4. Click "Deploy"

Railway will:
- Auto-detect it's a Python project
- Read your `Procfile`
- Start building your app

### 3.3 Add Environment Variables

Once your project is created:

1. Go to your Railway dashboard
2. Click on your project
3. Go to "Variables" tab
4. Add these variables:

```
SQLALCHEMY_DATABASE_URL=postgresql://user:password@localhost/subtrack
# Railway provides this, copy it from PostgreSQL service
```

### 3.4 Add PostgreSQL Database (Optional but Recommended)

1. In Railway dashboard, click "Add Service"
2. Select "PostgreSQL"
3. Railway automatically sets `DATABASE_URL` environment variable
4. Your app can use this automatically

**Or stick with SQLite:**
- Leave `SQLALCHEMY_DATABASE_URL` empty
- App uses SQLite by default

---

## Phase 4: Test Your Deployment

### 4.1 Get Your App URL

1. In Railway dashboard
2. Look for "Deployment" tab
3. Your app URL appears in the domains section (e.g., `https://subtrack-prod.railway.app`)

### 4.2 Test the App

1. Visit your URL
2. You should see SubTrack dashboard
3. Create a test category and customer
4. Verify everything works

### 4.3 Check Logs

If something doesn't work:
1. Go to "Logs" tab in Railway
2. Look for error messages
3. Common issues:
   - Database connection failed → Check `DATABASE_URL`
   - Port binding error → Check `Procfile`
   - Module not found → Check `requirements.txt`

---

## Phase 5: Continuous Deployment (Auto-Updates)

Once set up, Railway automatically:
- Watches your GitHub repository
- Rebuilds when you push changes
- Zero-downtime deployments

### To Update Your App

```powershell
# Make changes locally
git add .
git commit -m "Your changes"
git push origin main

# Railway automatically deploys within 1-2 minutes
```

---

## Troubleshooting

### App won't start
```
Check logs: Railway Dashboard → Logs tab
Common fixes:
- Verify Procfile is in project root
- Check requirements.txt has all dependencies
- Ensure no import errors in code
```

### Database issues
```
If using SQLite:
- Data persists only during deployment
- Resets on Railway redeploys
- Use PostgreSQL for persistent data

If using PostgreSQL:
- Run migrations: Railway console → python -m alembic upgrade head
- Check DATABASE_URL is set
```

### Port binding issues
```
Your Procfile should use $PORT variable:
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Alternative: Use Render Instead

If Railway has issues, try **Render** (very similar):

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your `subtrack` repo
5. Set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Deploy!

---

## What About Netlify?

**Short answer:** Netlify won't work for your full-stack app.

**Why?**
- Netlify only hosts static files (HTML/CSS/JS)
- Your Python backend runs on a server
- Netlify has no Python runtime

**Could you use it?**
- Only if you separated your frontend (React/Vue) from backend
- Would need to host backend elsewhere anyway
- More complex than Railway/Render

**Recommendation:** Stick with Railway for simplicity.

---

## Summary

| Step | Action | Time |
|------|--------|------|
| 1 | Push code to GitHub | 5 min |
| 2 | Create Railway account | 2 min |
| 3 | Connect GitHub repo | 2 min |
| 4 | Configure environment | 3 min |
| 5 | Deploy | Auto |
| **Total** | | **~15 minutes** |

Your app will be live at `https://subtrack-XXXX.railway.app` ✅

---

## Need Help?

- Railway Docs: https://docs.railway.app
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- GitHub Push Help: https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository
