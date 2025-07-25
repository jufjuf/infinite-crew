# API Reference

## Master Orchestrator API

### Functions

#### `init_database()`

Initializes the PostgreSQL database schema.

```python
init_database()
```

#### `spawn_task(prompt, parent_id=None, depth=0)`

Adds a new task to the Redis queue.

**Parameters:**
- `prompt` (str): Task description
- `parent_id` (str, optional): UUID of parent task
- `depth` (int): Task depth in hierarchy

**Returns:**
- `task_id` (str): UUID of created task

```python
task_id = spawn_task(
    "Write a blog post about AI",
    parent_id="123e4567-e89b-12d3-a456-426614174000",
    depth=1
)
```

#### `decompose(user_prompt)`

Breaks a complex task into subtasks using LLM.

**Parameters:**
- `user_prompt` (str): Task to decompose

**Returns:**
- `subtasks` (list): Array of subtask descriptions

```python
subtasks = decompose("Create a business plan for a startup")
# Returns: ["Research market", "Define product", "Financial projections", "Marketing strategy"]
```

#### `run_master(user_prompt)`

Main entry point for task execution.

**Parameters:**
- `user_prompt` (str): Mission to execute

```python
run_master("Analyze competitor landscape and create a report")
```

## Worker API

### Functions

#### `execute_task(prompt)`

Executes a single task using CrewAI.

**Parameters:**
- `prompt` (str): Task description

**Returns:**
- `result` (str): Task output

```python
result = execute_task("Research latest AI trends")
```

#### `process_single_task()`

Processes one task from the queue.

**Returns:**
- `success` (bool): Whether task was processed

## Data Structures

### Task Queue Entry

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "parent_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "prompt": "Research quantum computing applications",
  "depth": 1
}
```

### Database Schema

```sql
CREATE TABLE results (
    id UUID PRIMARY KEY,
    parent_id UUID REFERENCES results(id),
    prompt TEXT NOT NULL,
    output TEXT,
    depth INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Environment Variables

### Required

- `OPENAI_API_BASE`: LLM API endpoint
- `OPENAI_API_KEY`: API authentication key
- `REDIS_URL`: Redis connection string
- `DATABASE_URL`: PostgreSQL connection string

### Optional

- `CREWAI_MODEL_NAME`: LLM model to use (default: Mixtral-8x7B)
- `MAX_DEPTH`: Maximum task recursion depth (default: 2)
- `REFINEMENT_THRESHOLD`: Minimum output length for refinement (default: 500)

## Redis Commands

### Queue Operations

```bash
# Add task
LPUSH tasks '{"task_id":"...","prompt":"..."}'

# Get task (blocking)
BRPOP tasks 60

# Queue length
LLEN tasks

# View queue
LRANGE tasks 0 -1
```

## PostgreSQL Queries

### Useful Queries

```sql
-- Task statistics
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN output IS NOT NULL THEN 1 END) as completed,
    AVG(depth) as avg_depth
FROM results;

-- Task hierarchy
WITH RECURSIVE task_tree AS (
    SELECT * FROM results WHERE parent_id IS NULL
    UNION ALL
    SELECT r.* FROM results r
    JOIN task_tree t ON r.parent_id = t.id
)
SELECT * FROM task_tree ORDER BY depth;

-- Recent completions
SELECT prompt, output, created_at
FROM results
WHERE output IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;
```

## REST API (Future)

Planned REST API endpoints:

```
POST   /api/v1/missions       # Submit new mission
GET    /api/v1/missions/{id}  # Get mission status
GET    /api/v1/tasks          # List all tasks
GET    /api/v1/tasks/{id}     # Get task details
DELETE /api/v1/tasks/{id}     # Cancel task
GET    /api/v1/stats          # System statistics
```