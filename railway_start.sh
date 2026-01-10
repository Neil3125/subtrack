#!/bin/bash
set -e

echo "🚀 Starting SubTrack deployment on Railway..."

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Initialize authentication (creates admin user if needed)
echo "🔐 Initializing authentication..."
python init_auth.py

# Seed database with sample data (only if empty)
echo "🌱 Seeding database with sample data..."
python seed_data.py

# Start the application
echo "✅ Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
