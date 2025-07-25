#!/usr/bin/env python3
"""
Test database and Redis connections
"""

import os
import sys
import redis
import psycopg2
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing Infinite Crew connections...\n")

# Test Redis
print("1. Testing Redis connection...")
try:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url)
    
    # Test basic operations
    redis_client.set("test_key", "test_value")
    value = redis_client.get("test_key").decode('utf-8')
    
    if value == "test_value":
        print("✅ Redis connection successful")
        print(f"   URL: {redis_url}")
        
        # Test queue operations
        test_task = {"task_id": "test-123", "prompt": "Test task"}
        redis_client.lpush("test_queue", json.dumps(test_task))
        retrieved = json.loads(redis_client.rpop("test_queue"))
        
        if retrieved["task_id"] == "test-123":
            print("✅ Redis queue operations working")
        else:
            print("❌ Redis queue operations failed")
    else:
        print("❌ Redis connection failed: value mismatch")
    
    # Cleanup
    redis_client.delete("test_key")
    
except Exception as e:
    print(f"❌ Redis connection failed: {e}")

print("\n2. Testing PostgreSQL connection...")
try:
    db_url = os.getenv("DATABASE_URL", "postgresql://infinitecrew:infinitecrew@localhost:5432/infinitecrew")
    pg = psycopg2.connect(db_url)
    
    print("✅ PostgreSQL connection successful")
    print(f"   URL: {db_url.split('@')[1]}")  # Hide password
    
    # Test query
    with pg.cursor() as cur:
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"   Version: {version.split(',')[0]}")
        
        # Check if tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        if 'results' in tables:
            print("✅ Database schema initialized")
            
            # Get table info
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'results'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()
            print("   Results table columns:")
            for col_name, col_type in columns:
                print(f"     - {col_name}: {col_type}")
        else:
            print("⚠️  Database schema not initialized. Run init_database()")
    
    pg.close()
    
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")

print("\n3. Testing OpenAI/Together API configuration...")
api_base = os.getenv("OPENAI_API_BASE", "Not set")
api_key = os.getenv("OPENAI_API_KEY", "Not set")
model = os.getenv("CREWAI_MODEL_NAME", "Not set")

if api_base != "Not set":
    print(f"✅ API Base URL: {api_base}")
else:
    print("❌ API Base URL not configured")

if api_key != "Not set" and api_key != "<your_together_key>":
    print(f"✅ API Key: {'*' * 20}...")
else:
    print("❌ API Key not configured")

if model != "Not set":
    print(f"✅ Model: {model}")
else:
    print("❌ Model not configured")

print("\n" + "="*60)
print("Connection tests complete!")

if api_key == "Not set" or api_key == "<your_together_key>":
    print("\n⚠️  Don't forget to set your Together API key in the .env file!")
