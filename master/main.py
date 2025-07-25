import os
import uuid
import json
import redis
import psycopg2
import openai
from crewai import Agent, Task, Crew
import time

# Initialize connections
redis_client = redis.from_url(os.getenv("REDIS_URL"))
pg = psycopg2.connect(os.getenv("DATABASE_URL"))

# Configure OpenAI/Together
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")

def init_database():
    """Initialize the database schema if it doesn't exist"""
    with pg.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id UUID PRIMARY KEY,
                parent_id UUID REFERENCES results(id),
                prompt TEXT,
                output TEXT,
                depth INT,
                created_at TIMESTAMPTZ DEFAULT now()
            );
        """)
    pg.commit()

def spawn_task(prompt, parent_id=None, depth=0):
    """Add a new task to the Redis queue"""
    tid = str(uuid.uuid4())
    task_data = {
        "task_id": tid,
        "parent_id": parent_id,
        "prompt": prompt,
        "depth": depth
    }
    redis_client.lpush("tasks", json.dumps(task_data))
    print(f"Spawned task {tid}: {prompt[:50]}...")
    return tid

def decompose(user_prompt):
    """Use TogetherAI to break prompt into 1-4 sub-tasks"""
    messages = [
        {
            "role": "system", 
            "content": """Break the following user request into 1-4 simpler sub-tasks.
            If the task is already simple enough, return a JSON array with just that one task.
            Otherwise, break it down into logical, sequential sub-tasks.
            Return ONLY a JSON array of strings, no explanation.
            Example: ["Research X", "Analyze findings", "Write summary"]"""
        },
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model=os.getenv("CREWAI_MODEL_NAME", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
            messages=messages,
            temperature=0.2,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        # Clean up response if needed
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        subtasks = json.loads(content.strip())
        return subtasks if isinstance(subtasks, list) else [user_prompt]
    except Exception as e:
        print(f"Error decomposing task: {e}")
        # Fallback: return original prompt as single task
        return [user_prompt]

def check_completion(parent_id):
    """Check if all subtasks of a parent are complete"""
    with pg.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM results 
            WHERE parent_id = %s AND output IS NOT NULL
        """, (parent_id,))
        completed = cur.fetchone()[0]
        
        # Check if there are any pending tasks
        pending_tasks = []
        for i in range(redis_client.llen("tasks")):
            task = json.loads(redis_client.lindex("tasks", i))
            if task.get("parent_id") == parent_id:
                pending_tasks.append(task)
        
        return len(pending_tasks) == 0 and completed > 0

def run_master(user_prompt):
    """Main orchestration logic"""
    print(f"\nReceived mission: {user_prompt}")
    
    # Decompose the task
    subs = decompose(user_prompt)
    print(f"Decomposed into {len(subs)} sub-tasks")
    
    if len(subs) == 1:
        # Simple task - execute directly
        spawn_task(subs[0])
    else:
        # Complex task - create parent and spawn subtasks
        parent = spawn_task(user_prompt, depth=0)  # Meta task
        for i, sub in enumerate(subs):
            spawn_task(sub, parent_id=parent, depth=1)
            time.sleep(0.1)  # Small delay to avoid overwhelming

def monitor_loop():
    """Monitor task completion and spawn new tasks if needed"""
    print("Starting master orchestrator monitor loop...")
    
    while True:
        try:
            # Check queue status
            queue_size = redis_client.llen("tasks")
            print(f"\nQueue size: {queue_size}")
            
            # Check for completed parent tasks that might need synthesis
            with pg.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT parent_id FROM results 
                    WHERE parent_id IS NOT NULL 
                    AND parent_id NOT IN (
                        SELECT id FROM results WHERE output IS NOT NULL
                    )
                """)
                incomplete_parents = cur.fetchall()
                
                for (parent_id,) in incomplete_parents:
                    if check_completion(parent_id):
                        print(f"Parent {parent_id} subtasks complete, spawning synthesis task")
                        spawn_task(
                            f"Synthesize the results of subtasks for parent task {parent_id}",
                            parent_id=parent_id,
                            depth=2
                        )
            
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"Monitor loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Start with a user prompt if provided
    import sys
    if len(sys.argv) > 1:
        user_mission = " ".join(sys.argv[1:])
        run_master(user_mission)
    else:
        # Interactive mode
        print("Master Orchestrator started in interactive mode")
        print("Enter 'monitor' to start monitoring loop, or type a mission:")
        
        user_input = input("Mission: ")
        if user_input.lower() == "monitor":
            monitor_loop()
        else:
            run_master(user_input)
            print("\nMission queued! Starting monitor loop...")
            monitor_loop()
