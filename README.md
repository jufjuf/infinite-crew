# 🚀 Infinite Crew - Autonomous Agent Stack on Railway

[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-blueviolet)](https://railway.app)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.30.0-green.svg)](https://github.com/joaomdmoura/crewAI)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🤖 Overview

Infinite Crew is a self-scaling agent system that can recursively break down complex tasks into sub-tasks, spawn Docker-based CrewAI agents on Railway, and orchestrate them to completion. Think of it as **agents that create agents** - a truly autonomous system that scales with task complexity.

### ✨ Key Features

- **Recursive Task Decomposition**: Automatically breaks complex missions into manageable sub-tasks
- **Auto-Scaling Workers**: Spawns CrewAI agents on-demand using Railway's container infrastructure
- **Hierarchical Execution**: Maintains parent-child relationships between tasks
- **Real-Time Monitoring**: Beautiful Streamlit UI to track progress and view results
- **Zero Infrastructure Management**: Fully managed on Railway with Redis and PostgreSQL

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│Master Orchestrator│◀───│  Redis Queue    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                          │
                               ▼                          ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │ CrewAI Workers  │
                        │   (Results)     │◀────│   (Docker)      │
                        └─────────────────┘     └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- [Railway account](https://railway.app) (free tier works!)
- [TogetherAI API key](https://api.together.xyz/) for LLM access
- Docker installed locally
- Node.js (for Railway CLI)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/jufjuf/infinite-crew
cd infinite-crew

# Install Railway CLI
npm install -g @railway/cli
railway login

# Copy environment template
cp .env.template .env
# Edit .env with your TogetherAI API key
```

### 2. Deploy to Railway

```bash
# Run the deployment script
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Or manually:

```bash
# Initialize Railway project
railway init

# Add databases
railway add --service --database Redis
railway add --service --database PostgreSQL

# Deploy services
railway up
```

### 3. Configure Environment Variables

In your Railway dashboard, set these variables:

- `OPENAI_API_KEY`: Your TogetherAI API key
- `OPENAI_API_BASE`: `https://api.together.xyz/v1`
- `CREWAI_MODEL_NAME`: `mistralai/Mixtral-8x7B-Instruct-v0.1`

### 4. Access the UI

Visit your Railway-generated domain to access the Streamlit interface.

## 💻 Local Development

For local development with hot-reload:

```bash
# Setup local environment
chmod +x scripts/local-dev.sh
./scripts/local-dev.sh

# Access UI at http://localhost:8501
```

## 📝 Example Usage

### Simple Task
```python
"Write a haiku about artificial intelligence"
```

### Complex Mission
```python
"Create a comprehensive business plan for an AI-powered education startup:
1. Market analysis and competitor research
2. Product development roadmap
3. Financial projections for 3 years
4. Go-to-market strategy
5. Team structure and hiring plan"
```

The system will:
1. Break this into sub-tasks
2. Spawn specialized agents for each task
3. Execute them in parallel
4. Synthesize results
5. Potentially spawn refinement tasks

## 📊 Monitoring

- **Queue Status**: Check Redis with `railway redis-cli llen tasks`
- **Live Logs**: View in Railway dashboard or `railway logs`
- **Results**: Query PostgreSQL or use the Streamlit UI
- **Task Tree**: Visualize task hierarchies in the UI

## 🛠️ Configuration

### Scaling Parameters

Edit `worker/worker.py`:
- `MAX_DEPTH`: Maximum recursion depth (default: 2)
- `REFINEMENT_THRESHOLD`: Minimum output length for refinement (default: 500)

### Model Selection

Change `CREWAI_MODEL_NAME` to use different models:
- `mistralai/Mixtral-8x7B-Instruct-v0.1` (default)
- `meta-llama/Llama-2-70b-chat-hf`
- `NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO`

## 📁 Project Structure

```
infinite-crew/
├── master/           # Orchestrator service
│   ├── main.py      # Task decomposition & monitoring
│   └── Dockerfile
├── worker/          # CrewAI worker service  
│   └── worker.py    # Task execution logic
├── ui/              # Streamlit interface
│   └── app.py       # Web dashboard
├── scripts/         # Deployment & dev tools
├── examples/        # Usage examples
└── tests/          # Test suite
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Priority Areas

- 🔄 Retry logic and error handling
- 📈 Cost tracking and optimization
- 🔌 Webhook integrations
- 🎯 Task prioritization
- 💾 Result caching

## 🐛 Troubleshooting

### Workers not starting
- Verify Docker image is pushed to GHCR
- Check Railway logs for pull errors

### Tasks stuck in queue
- Confirm API credentials are set
- Check worker logs for errors

### Database connection issues
- Verify `DATABASE_URL` in Railway
- Run `scripts/init.sql` manually if needed

## 📚 Resources

- [Architecture Deep Dive](ARCHITECTURE.md)
- [Railway Documentation](https://docs.railway.app)
- [CrewAI Documentation](https://github.com/joaomdmoura/crewAI)
- [TogetherAI Models](https://docs.together.ai/docs/inference-models)

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**Built with ❤️ using CrewAI and Railway**

*"Agents creating agents, turtles all the way down"* 🐢