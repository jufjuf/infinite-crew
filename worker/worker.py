import os
import json
import redis
import psycopg2
import openai
import sys
import time
from crewai import Agent, Task, Crew

# Initialize connections
redis_client = redis.from_url(os.getenv("REDIS_URL"))
pg = psycopg2.connect(os.getenv("DATABASE_URL"))

# Configure OpenAI/Together
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")

def execute_task(prompt):
    """Execute a single task using CrewAI"""
    print(f"Executing task: {prompt[:100]}...")
    
    try:
        # Create an agent
        agent = Agent(
            role="Autonomous Task Executor",
            goal=f"Complete this exact task: {prompt}",
            backstory="""You are a tireless agent capable of executing any task. 
                         You work methodically and produce high-quality results.
                         You complete tasks thoroughly and provide detailed outputs.""",
            llm_config={
                "model": os.getenv("CREWAI_MODEL_NAME", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
                "base_url": os.getenv("OPENAI_API_BASE"),
                "api_key": os.getenv("OPENAI_API_KEY")
            },
            verbose=True,
            allow_delegation=False
        )
        
        # Create a task
        task = Task(
            description=prompt,
            agent=agent,
            expected_output="A complete and detailed response to the task"
        )
        
        # Create and run crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=2
        )
        
        result = crew.kickoff()
        return str(result)
        
    except Exception as e:
        error_msg = f"Error executing task: {str(e)}"
        print(error_msg)
        return error_msg

def should_spawn_deeper_tasks(result, depth):
    """Determine if we should spawn deeper refinement tasks"""
    # Only spawn deeper tasks if:
    # 1. We're not too deep already (max depth 2)
    # 2. The result is substantial (>500 chars)
    # 3. The result might benefit from refinement
    
    if depth >= 2:
        return False
    
    if len(result) < 500:
        return False
    
    # Check if result indicates need for refinement
    refinement_indicators = [
        "needs further",
        "could be improved",
        "additional research",
        "more detail",
        "incomplete"
    ]
    
    result_lower = result.lower()
    return any(indicator in result_lower for indicator in refinement_indicators)

def spawn_refinement_task(prompt, result, task_id, depth):
    """Spawn a task to refine the current result"""
    refinement_prompt = f"""
    Refine and improve the following output:
    
    Original Task: {prompt}
    
    Current Output:
    {result[:1000]}{'...' if len(result) > 1000 else ''}
    
    Please enhance this output by:
    1. Adding more detail where needed
    2. Improving clarity and structure
    3. Ensuring completeness
    4. Correcting any errors or inconsistencies
    """
    
    # Import spawn_task from master
    sys.path.append('/app')
    from master.main import spawn_task
    
    new_task_id = spawn_task(
        refinement_prompt,
        parent_id=task_id,
        depth=depth + 1
    )
    
    print(f"Spawned refinement task: {new_task_id}")

def process_single_task():
    """Process one task from the queue"""
    print("Worker waiting for task...")
    
    # Blocking pop from Redis queue (timeout after 60 seconds)
    result = redis_client.brpop("tasks", timeout=60)
    
    if result is None:
        print("No tasks available after 60 seconds, exiting")
        return False
    
    _, job = result
    data = json.loads(job)
    
    print(f"\nProcessing task {data['task_id']}")
    print(f"Prompt: {data['prompt'][:200]}...")
    print(f"Depth: {data['depth']}")
    
    # Execute the task
    result = execute_task(data["prompt"])
    
    # Store result in database
    try:
        with pg.cursor() as cur:
            cur.execute("""
                INSERT INTO results(id, parent_id, prompt, output, depth)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data["task_id"],
                data.get("parent_id"),
                data["prompt"],
                result,
                data["depth"]
            ))
        pg.commit()
        print(f"Result stored for task {data['task_id']}")
        
        # Check if we should spawn deeper tasks
        if should_spawn_deeper_tasks(result, data["depth"]):
            spawn_refinement_task(
                data["prompt"],
                result,
                data["task_id"],
                data["depth"]
            )
        
        return True
        
    except Exception as e:
        print(f"Error storing result: {e}")
        pg.rollback()
        # Re-queue the task
        redis_client.lpush("tasks", job)
        return False

def main():
    """Main worker loop"""
    print("CrewAI Worker started")
    print(f"Connected to Redis: {os.getenv('REDIS_URL')[:30]}...")
    print(f"Connected to PostgreSQL: {os.getenv('DATABASE_URL')[:30]}...")
    print(f"Using model: {os.getenv('CREWAI_MODEL_NAME')}")
    
    # Process tasks until queue is empty or error
    while True:
        try:
            if not process_single_task():
                print("Worker shutting down")
                break
        except KeyboardInterrupt:
            print("\nWorker interrupted, shutting down")
            break
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()
