# SubTrack Web

A modern subscription tracking web application with AI-powered insights and relationship intelligence.

## Features

- 📊 **Subscription Management**: Track all your subscriptions with categories and groups
- 🤖 **AI Insights**: Get intelligent recommendations on renewals, cancellations, and cost optimization
- 🔗 **Relationship Intelligence**: Automatically discover connections between customers, subscriptions, and vendors
- 🔍 **Global Search**: Fast, fuzzy search across all your data
- 📱 **Responsive Design**: Clean, modern UI with smooth animations
- ♿ **Accessible**: Built with accessibility best practices

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **ORM**: SQLAlchemy + Alembic migrations
- **Frontend**: Jinja2 templates + HTMX + vanilla JS
- **Styling**: Custom CSS with design system

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

5. Initialize the database:
```bash
alembic upgrade head
python seed_data.py
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

7. Open your browser to: http://localhost:8000

## Configuration

### Database

- **Development**: Uses SQLite by default (`sqlite:///./subtrack.db`)
- **Production**: Set `DATABASE_URL` to your PostgreSQL connection string

### AI Features (Optional)

The app works perfectly without AI configured - it will use deterministic heuristics.

To enable AI features:
1. Get an OpenAI API key (or compatible provider)
2. Set in `.env`:
   - `SUBTRACK_AI_API_KEY=your-key`
   - `SUBTRACK_AI_MODEL=gpt-4` (or your preferred model)
   - `SUBTRACK_AI_BASE_URL=https://api.openai.com/v1` (or compatible endpoint)

## Project Structure

```
subtrack-web/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   ├── ai/                  # AI provider and intelligence
│   └── templates/           # Jinja2 templates
├── static/                  # CSS, JS, images
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt
└── README.md
```

## API Endpoints

### Web Routes
- `GET /` - Dashboard
- `GET /categories` - Categories list
- `GET /categories/{id}` - Category detail
- `GET /groups/{id}` - Group detail
- `GET /customers/{id}` - Customer detail
- `GET /subscriptions/{id}` - Subscription detail
- `GET /search` - Global search

### API Routes
- `POST /api/categories` - Create category
- `GET /api/categories` - List categories
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category
- *(Similar patterns for groups, customers, subscriptions)*

### AI Routes
- `POST /api/ai/insights` - Get AI-powered insights
- `POST /api/ai/link_analyze` - Analyze relationships
- `POST /api/links/{id}/decide` - Accept/reject link suggestion

## Testing

```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## License

MIT License - see LICENSE file for details
