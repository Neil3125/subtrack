# SubTrack Web - Run Instructions

## Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - The `.env` file is already configured for local development
   - To enable AI features, add your OpenAI API key:
     ```
     SUBTRACK_AI_API_KEY=your-api-key-here
     ```

3. **Initialize Database**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Seed with sample data
   python seed_data.py
   ```

4. **Start the Application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the Application**
   - Open your browser to: **http://localhost:8000**
   - The dashboard will load with sample data

### Sample Data Included

The seed script creates:
- **3 Categories**: Hosting & Infrastructure, Security & Antivirus, Productivity Tools
- **2 Groups**: VPS Servers, Shared Hosting
- **6 Customers**: Including Acme Corp, TechStart Inc, Digital Agency Pro, etc.
- **11 Subscriptions**: Various subscriptions across categories with different renewal dates

### Key Features to Test

#### 1. Dashboard
- View active subscriptions count
- See total monthly costs
- Check expiring soon and overdue subscriptions
- Click "Refresh" in the AI Insights card to generate insights

#### 2. AI Features
- **AI Insights**: Click refresh buttons on dashboard, category, or customer pages
  - Works without API key (deterministic mode)
  - With API key: Get AI-powered recommendations and summaries
  
- **Link Analysis**: Click "🔗 Analyze Links" in the navbar
  - Discovers relationships between customers based on:
    - Same email domains
    - Similar names
    - Shared phone numbers
    - Matching tags
    - Same vendors/plans
    - Similar renewal patterns

#### 3. Navigation
- **Categories**: Browse all categories or click specific ones from sidebar
- **Groups**: View groups within categories
- **Customers**: See customer details and their subscriptions
- **Subscriptions**: View detailed subscription information

#### 4. Search
- Use the global search in the navbar
- Real-time search across all entities
- Results appear as you type (300ms debounce)

#### 5. Connections Panel
- On customer detail pages, click "Refresh" in the Connections panel
- See AI-discovered relationships with other customers
- Accept or reject link suggestions (updates immediately)

### API Endpoints

The application provides both web UI and REST API:

#### Web Routes
- `GET /` - Dashboard
- `GET /categories` - Categories list
- `GET /categories/{id}` - Category detail
- `GET /groups/{id}` - Group detail
- `GET /customers/{id}` - Customer detail
- `GET /subscriptions/{id}` - Subscription detail

#### REST API
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category
- `GET /api/subscriptions` - List subscriptions
- `POST /api/ai/insights` - Generate AI insights
- `POST /api/ai/link_analyze` - Analyze relationships
- `GET /api/search?q=query` - Global search

Full API documentation available at: **http://localhost:8000/docs**

### Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_expiry_calculations.py -v
```

All 14 tests should pass:
- 8 tests for expiry calculations
- 6 tests for link intelligence heuristics

### Production Deployment

For production:

1. **Update Environment Variables**
   ```bash
   DATABASE_URL=postgresql://user:password@localhost/subtrack
   SECRET_KEY=your-strong-secret-key
   DEBUG=false
   ```

2. **Use PostgreSQL**
   - The app supports both SQLite (dev) and PostgreSQL (prod)
   - Database URL is auto-detected from environment

3. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start with Production Server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Troubleshooting

**Database Issues**
```bash
# Reset database
rm subtrack.db
alembic upgrade head
python seed_data.py
```

**Port Already in Use**
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Architecture Overview

```
subtrack-web/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API routes
│   ├── ai/                  # AI provider & intelligence
│   │   ├── provider.py      # OpenAI integration
│   │   ├── insights.py      # Insights analyzer
│   │   └── link_intelligence.py  # Relationship discovery
│   └── templates/           # Jinja2 templates
├── static/
│   ├── css/style.css        # Design system
│   └── js/app.js            # JavaScript utilities
├── alembic/                 # Database migrations
└── tests/                   # Test suite
```

### Key Technologies

- **Backend**: FastAPI (Python)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy with Alembic migrations
- **Frontend**: Jinja2 templates + HTMX + vanilla JS
- **Styling**: Custom CSS with design system
- **AI**: OpenAI-compatible API (optional)

### Design System

The UI uses a consistent design system with:
- **Typography scale**: 8 sizes from xs (12px) to 4xl (36px)
- **Spacing scale**: 12 values from 1 (4px) to 16 (64px)
- **Color palette**: Primary, success, warning, danger, info
- **Components**: Cards, buttons, forms, tables, badges
- **Animations**: Smooth transitions (150-350ms)
- **Responsive**: Mobile-first with breakpoints

### AI Features Detail

#### Without API Key (Deterministic Mode)
- Expiry calculations
- Cost analysis by vendor/category
- Heuristic-based relationship discovery
- Basic recommendations

#### With API Key (AI-Enhanced Mode)
- Natural language summaries
- Intelligent recommendations
- Risk flag analysis
- Enhanced confidence scoring for relationships
- Evidence explanations

### Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API docs at `/docs`
3. Examine logs for error details

---

**🎉 Enjoy using SubTrack Web!**

Built with ❤️ using FastAPI, HTMX, and modern web technologies.
