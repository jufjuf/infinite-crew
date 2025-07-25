# Infinite Crew - Autonomous Agent Stack on Railway

## Overview

Infinite Crew is a self-scaling agent system that can recursively break down complex tasks into sub-tasks, spawn Docker-based CrewAI agents on Railway, and orchestrate them to completion.

## Architecture

1. **Master Orchestrator**: Always-on service that decomposes tasks
2. **Task Queue**: Redis-based queue for distributing work
3. **Result Store**: PostgreSQL database for storing outputs
4. **Sub-Agent Workers**: Ephemeral Railway services that execute tasks
5. **Docker Base Image**: Shared image for all workers

## Setup Instructions

### Prerequisites

- Railway account (free tier works)
- TogetherAI API key
- Docker installed locally
- Railway CLI installed: `npm i -g @railway/cli`
- GitHub Container Registry access

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/jufjuf/infinite-crew
cd infinite-crew
```

2. Install Railway CLI and login:
```bash
railway login
```

3. Initialize Railway project:
```bash
railway init
railway add --service --database Redis
railway add --service --database PostgreSQL
```

4. Build and push Docker image:
```bash
docker build -f Dockerfile.worker -t ghcr.io/jufjuf/crew-worker:latest .
docker push ghcr.io/jufjuf/crew-worker:latest
```

5. Deploy services:
```bash
# Deploy master orchestrator
railway add --service --name master
railway up --service master

# Deploy worker template
railway add --service --name crew-worker --image ghcr.io/jufjuf/crew-worker:latest

# Deploy UI (optional)
railway add --service --name ui
railway up --service ui
```

6. Configure environment variables in Railway dashboard

7. Create the database schema:
```sql
CREATE TABLE results (
    id UUID PRIMARY KEY,
    parent_id UUID REFERENCES results(id),
    prompt TEXT,
    output TEXT,
    depth INT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

## Usage

Access the Streamlit UI at your Railway-generated domain and enter a mission. The system will:

1. Break down your request into sub-tasks
2. Spawn worker containers for each task
3. Store results in PostgreSQL
4. Recursively create deeper tasks if needed

## Environment Variables

- `OPENAI_API_BASE`: TogetherAI endpoint
- `OPENAI_API_KEY`: Your TogetherAI API key
- `CREWAI_MODEL_NAME`: Model to use (default: Mixtral-8x7B)
- `REDIS_URL`: Automatically set by Railway
- `DATABASE_URL`: Automatically set by Railway
- `RAILWAY_TOKEN`: For programmatic deployments

## Monitoring

- Check Redis queue: `railway redis-cli llen tasks`
- View Railway logs for each service
- Query PostgreSQL for results

## License

MIT