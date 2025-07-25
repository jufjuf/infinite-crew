#!/usr/bin/env python3
"""
Example: Running a complex multi-step mission through Infinite Crew
"""

import os
import sys
import time
import json

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

# Complex mission
complex_mission = """
Create a comprehensive guide for starting a tech startup:
1. Research current market trends in AI and sustainability
2. Develop a unique business idea combining both fields
3. Create a business plan with financial projections
4. Design a minimum viable product (MVP) specification
5. Write a pitch deck outline for investors
"""

print(f"Launching complex mission:\n{complex_mission}")
run_master(complex_mission)

print("\nMission launched! Monitoring task decomposition...")

# Monitor task creation
time.sleep(2)  # Give time for decomposition

# Show task tree
print("\nTask Tree:")
tasks = []
for i in range(redis_client.llen("tasks")):
    task_json = redis_client.lindex("tasks", i)
    if task_json:
        task = json.loads(task_json)
        tasks.append(task)
        indent = "  " * task['depth']
        print(f"{indent}└─ [{task['depth']}] {task['prompt'][:80]}...")

print(f"\nTotal tasks created: {len(tasks)}")

# Monitor progress with visual indicator
print("\nProgress:")
start_time = time.time()
max_time = 300  # 5 minutes max

while time.time() - start_time < max_time:
    queue_size = redis_client.llen("tasks")
    
    with pg.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM results WHERE output IS NOT NULL")
        completed = cur.fetchone()[0]
    
    # Progress bar
    total = len(tasks)
    progress = completed / total if total > 0 else 0
    bar_length = 40
    filled = int(bar_length * progress)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    print(f"\r[{bar}] {completed}/{total} tasks | Queue: {queue_size} | Time: {int(time.time() - start_time)}s", end="")
    
    if queue_size == 0 and completed >= total:
        print("\n✅ Mission complete!")
        break
    
    time.sleep(1)

print("\n\nFinal Results Summary:")

# Show results hierarchy
with pg.cursor() as cur:
    cur.execute("""
        WITH RECURSIVE task_tree AS (
            SELECT id, parent_id, prompt, output, depth
            FROM results
            WHERE parent_id IS NULL
            
            UNION ALL
            
            SELECT r.id, r.parent_id, r.prompt, r.output, r.depth
            FROM results r
            JOIN task_tree t ON r.parent_id = t.id
        )
        SELECT * FROM task_tree
        ORDER BY depth, id
    """)
    results = cur.fetchall()
    
    for task_id, parent_id, prompt, output, depth in results:
        indent = "  " * depth
        status = "✅" if output else "⏳"
        print(f"\n{indent}{status} [{depth}] {prompt[:100]}...")
        if output:
            preview = output[:200].replace('\n', ' ')
            print(f"{indent}   → {preview}...")

print("\n" + "="*80)
print("Mission execution complete! Check the UI for full results.")
