#!/bin/bash

# Local Development Setup Script

set -e

echo "💻 Starting Infinite Crew in local development mode..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your API keys before continuing."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check for required environment variables
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "<your_together_key>" ]; then
    echo "❌ Please set your OPENAI_API_KEY in the .env file"
    exit 1
fi

# Start services with docker-compose
echo "🐳 Starting Docker services..."
docker-compose up -d redis postgres

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Run database initialization
echo "🗍 Initializing database..."
docker-compose exec -T postgres psql -U infinitecrew -d infinitecrew < scripts/init.sql

# Start application services
echo "🚀 Starting application services..."
docker-compose up -d master worker ui

# Show logs
echo ""
echo "✅ Local development environment started!"
echo ""
echo "🔗 Access points:"
echo "   - Streamlit UI: http://localhost:8501"
echo "   - Redis: localhost:6379"
echo "   - PostgreSQL: localhost:5432 (user: infinitecrew, password: infinitecrew)"
echo ""
echo "📊 View logs:"
echo "   - All services: docker-compose logs -f"
echo "   - Master only: docker-compose logs -f master"
echo "   - Workers only: docker-compose logs -f worker"
echo ""
echo "🛑 Stop all services:"
echo "   - docker-compose down"
echo ""