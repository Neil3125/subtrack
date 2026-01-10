# SubTrack Web - Quick Start ⚡

## Installation (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database with sample data
alembic upgrade head
python seed_data.py

# 3. Start the application
python start.py
```

## Access

Open your browser to: **http://localhost:8000**

## What's Included

✅ **3 Categories** - Hosting, Security, Productivity  
✅ **6 Customers** - Including Acme Corp, TechStart Inc, etc.  
✅ **11 Subscriptions** - Various renewal dates (some expiring soon!)  
✅ **AI Features** - Works without API key (deterministic mode)  

## First Steps

1. **Explore Dashboard** - See stats and expiring subscriptions
2. **Click "Refresh" in AI Insights** - Generate insights (works without API key!)
3. **Browse Categories** - Click on sidebar categories
4. **Try Global Search** - Type anything in the top search bar
5. **Click "🔗 Analyze Links"** - Discover relationships between customers

## Key Features to Test

### 🤖 AI Insights
- Dashboard → Click "Refresh" in AI Insights card
- Category pages → Generate category-specific insights
- Customer pages → Get personalized recommendations

### 🔗 Relationship Discovery
- Navbar → Click "🔗 Analyze Links"
- Discovers connections based on:
  - Same email domains
  - Similar names
  - Shared vendors
  - Matching tags

### 🔍 Search
- Type in navbar search
- Live results as you type
- Searches across all entities

### 📊 Dashboard Metrics
- **Active Subscriptions**: Total count
- **Monthly Cost**: Sum of all active subscriptions
- **Expiring Soon**: Renewals within 30 days
- **Overdue**: Past due subscriptions (1 included in sample data!)

## Sample Data Preview

**Categories:**
1. Hosting & Infrastructure
2. Security & Antivirus
3. Productivity Tools

**Notable Subscriptions:**
- DigitalOcean - Expiring in 5 days ⚠️
- Cloudflare - **OVERDUE** by 2 days 🚨
- AWS - Expiring in 15 days
- ESET (2 instances) - Same vendor, different customers
- Microsoft 365 - $1,200/month
- Namecheap - **OVERDUE** by 15 days 🚨

**Cross-Category Links:**
- Acme Corp appears in both Hosting AND Security categories
- Same email domain (acmecorp.com) with different divisions

## Enable Full AI Features (Optional)

Add to `.env` file:
```
SUBTRACK_AI_API_KEY=your-openai-api-key-here
```

With API key enabled:
- Natural language summaries
- Intelligent recommendations
- Enhanced relationship analysis
- Risk flag detection

**Without API key, the app still works great with deterministic analysis!**

## API Documentation

Interactive API docs: **http://localhost:8000/docs**

## File Structure (Simplified)

```
subtrack-web/
├── app/               # Backend code
│   ├── main.py        # FastAPI app
│   ├── models/        # Database models
│   ├── routers/       # API endpoints
│   ├── ai/            # AI intelligence
│   └── templates/     # HTML views
├── static/            # CSS & JavaScript
├── tests/             # Test suite
├── start.py           # Start script
└── seed_data.py       # Sample data
```

## Running Tests

```bash
pytest
```

All 14 tests should pass! ✅

## Troubleshooting

**Port already in use?**
```bash
uvicorn app.main:app --port 8001
```

**Reset database?**
```bash
rm subtrack.db
alembic upgrade head
python seed_data.py
```

**Import errors?**
```bash
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. ✅ Add your own categories
2. ✅ Create customer records
3. ✅ Track subscriptions
4. ✅ Use AI insights to optimize costs
5. ✅ Discover hidden relationships

## Need Help?

- 📖 See `README.md` for overview
- 📋 See `RUN_INSTRUCTIONS.md` for detailed setup
- 📊 See `PROJECT_SUMMARY.md` for complete feature list
- 📚 Visit `/docs` for API documentation

---

**🎉 Ready to track subscriptions like a pro!**
