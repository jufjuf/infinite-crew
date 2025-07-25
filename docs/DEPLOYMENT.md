# Deployment Guide

## Railway Deployment (Recommended)

### Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **TogetherAI API Key**: Get from [api.together.xyz](https://api.together.xyz)
3. **GitHub Account**: For container registry

### Step-by-Step Deployment

#### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/infinite-crew
cd infinite-crew
```

#### 2. Install Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (via npm)
npm install -g @railway/cli
```

#### 3. Login to Railway

```bash
railway login
```

#### 4. Create Railway Project

```bash
railway init
# Choose "Empty Project"
```

#### 5. Add Databases

```bash
# Add Redis
railway add --database redis

# Add PostgreSQL  
railway add --database postgresql
```

#### 6. Deploy Services

```bash
# Deploy Master Orchestrator
railway add --service --name master
railway link master
railway up

# Deploy UI
railway add --service --name ui
railway link ui
railway up
```

#### 7. Configure Worker Service

In Railway dashboard:

1. Click "New Service" → "Docker Image"
2. Image: `ghcr.io/YOUR_USERNAME/crew-worker:latest`
3. Name: `worker`
4. Settings:
   - Restart Policy: `ON_FAILURE`
   - Max Restarts: `0`

#### 8. Set Environment Variables

In Railway dashboard for each service:

```env
OPENAI_API_BASE=https://api.together.xyz/v1
OPENAI_API_KEY=your_together_key
CREWAI_MODEL_NAME=mistralai/Mixtral-8x7B-Instruct-v0.1
```

#### 9. Build and Push Docker Image

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Build and push
docker build -f Dockerfile.worker -t ghcr.io/YOUR_USERNAME/crew-worker:latest .
docker push ghcr.io/YOUR_USERNAME/crew-worker:latest
```

#### 10. Initialize Database

Connect to PostgreSQL via Railway dashboard and run:

```sql
CREATE TABLE IF NOT EXISTS results (
    id UUID PRIMARY KEY,
    parent_id UUID REFERENCES results(id),
    prompt TEXT NOT NULL,
    output TEXT,
    depth INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Troubleshooting

#### Worker containers not starting

1. Check Docker image is public or Railway has access
2. Verify environment variables are set
3. Check Railway logs: `railway logs worker`

#### Database connection errors

1. Ensure services are in same Railway project
2. Check connection strings in environment
3. Verify database is initialized

#### High costs

1. Set worker scaling limits
2. Use smaller LLM models
3. Implement task caching

## Alternative Deployments

### Docker Swarm

```yaml
# docker-stack.yml
version: '3.8'

services:
  master:
    image: ghcr.io/YOUR_USERNAME/crew-master:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: any

  worker:
    image: ghcr.io/YOUR_USERNAME/crew-worker:latest
    deploy:
      replicas: 5
      restart_policy:
        condition: on-failure
        max_attempts: 0
```

Deploy: `docker stack deploy -c docker-stack.yml infinite-crew`

### Kubernetes

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crew-worker
spec:
  replicas: 5
  selector:
    matchLabels:
      app: crew-worker
  template:
    metadata:
      labels:
        app: crew-worker
    spec:
      containers:
      - name: worker
        image: ghcr.io/YOUR_USERNAME/crew-worker:latest
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: crew-secrets
              key: redis-url
```

Deploy: `kubectl apply -f k8s-deployment.yaml`

## Production Considerations

### Security

1. **API Keys**: Use Railway's secret management
2. **Network**: Enable private networking between services
3. **Access**: Restrict UI access with authentication

### Monitoring

1. **Logs**: Aggregate with Datadog/LogDNA
2. **Metrics**: Export to Prometheus
3. **Alerts**: Set up for queue depth, error rates

### Scaling

1. **Workers**: Auto-scale based on queue depth
2. **Database**: Enable connection pooling
3. **Redis**: Consider Redis Cluster for high load

### Cost Optimization

1. **Model Selection**: Use smaller models for simple tasks
2. **Caching**: Cache repeated task results
3. **Timeouts**: Set aggressive timeouts on workers