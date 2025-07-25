#!/bin/bash

# Test script for local development

set -e

echo "🧪 Testing Infinite Crew locally..."

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Services not running. Start with: ./scripts/local-dev.sh"
    exit 1
fi

# Test connections
echo "\n1️⃣ Testing connections..."
docker-compose exec -T master python -c "
import redis
import psycopg2
import os

try:
    r = redis.from_url(os.getenv('REDIS_URL'))
    r.ping()
    print('✅ Redis connection: OK')
except Exception as e:
    print(f'❌ Redis connection: {e}')

try:
    pg = psycopg2.connect(os.getenv('DATABASE_URL'))
    pg.close()
    print('✅ PostgreSQL connection: OK')
except Exception as e:
    print(f'❌ PostgreSQL connection: {e}')
"

# Test task decomposition
echo "\n2️⃣ Testing task decomposition..."
docker-compose exec -T master python -c "
from main import decompose
result = decompose('Write a blog post about AI')
print(f'✅ Decomposition result: {result}')
"

# Submit a test task
echo "\n3️⃣ Submitting test task..."
docker-compose exec -T master python -c "
from main import run_master
run_master('Write a haiku about testing')
print('✅ Task submitted')
"

# Check queue
echo "\n4️⃣ Checking queue..."
QUEUE_SIZE=$(docker-compose exec -T redis redis-cli llen tasks | tr -d '')
echo "📊 Queue size: $QUEUE_SIZE"

# Wait for processing
echo "\n5️⃣ Waiting for task completion..."
sleep 10

# Check results
echo "\n6️⃣ Checking results..."
docker-compose exec -T postgres psql -U infinitecrew -d infinitecrew -c "
SELECT COUNT(*) as completed_tasks FROM results WHERE output IS NOT NULL;
"

echo "\n✅ All tests completed!"
echo "🌐 Visit http://localhost:8501 to see the UI"