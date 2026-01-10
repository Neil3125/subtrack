#!/bin/bash
set -e

echo "🚀 Starting SubTrack deployment on Railway..."

# Set default port if not provided
PORT=${PORT:-8000}
echo "📡 Using port: $PORT"

# Check if using PostgreSQL (Railway provides DATABASE_URL)
if [ -n "$DATABASE_URL" ]; then
    echo "✅ PostgreSQL detected - your data persists across deployments!"
    echo "   No manual backup/restore needed."
else
    echo "⚠️ Using SQLite - data will reset on each deployment"
    echo "   For persistent data, add PostgreSQL service in Railway dashboard"
fi

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head || echo "⚠️ Migration warning (may already be up to date)"

# Initialize authentication (creates admin user if needed)
echo "🔐 Initializing authentication..."
python init_auth.py || echo "⚠️ Auth init warning (may already be initialized)"

# Seed database with sample data (only if empty)
# This only runs if the database is empty, so it won't overwrite your data
echo "🌱 Checking if seed data is needed..."
python seed_data.py || echo "⚠️ Seed warning (may already be seeded)"

# Start the application
echo "✅ Starting application on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
