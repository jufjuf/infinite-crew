#!/usr/bin/env python3
"""
Example: Running a simple task through Infinite Crew
"""

import os
import sys
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from master.main import run_master, init_database
import redis
import psycopg2

# Initialize connections
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
pg = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://infinitecrew:infinitecrew@localhost:5432/infinitecrew"))

# Initialize database
init_database()

# Simple task
simple_task = "Write a haiku about artificial intelligence"

print(f"Launching simple task: {simple_task}")
run_master(simple_task)

print("\nTask queued! Monitoring progress...")

# Monitor progress
for i in range(30):  # Check for 30 seconds
    queue_size = redis_client.llen("tasks")
    
 n    with pg.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM results WHERE output IS NOT NULL")
        completed = cur.fetchone()[0]
    
    print(f"\rQueue: {queue_size} | Completed: {completed}", end="")
    
    if queue_size == 0 and completed > 0:
        break
    
    time.sleep(1)

print("\n\nResults:")

# Show results
with pg.cursor() as cur:
    cur.execute("""
        SELECT prompt, output, created_at 
        FROM results 
        WHERE output IS NOT NULL 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    results = cur.fetchall()
    
    for prompt, output, created_at in results:
        print(f"\n{'='*60}")
        print(f"Task: {prompt[:100]}...")
        print(f"Completed: {created_at}")
        print(f"Output:\n{output}")
