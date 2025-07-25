#!/bin/bash

# Infinite Crew Deployment Script

set -e

echo "🚀 Deploying Infinite Crew to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway first:"
    railway login
fi

# Initialize Railway project if not exists
if [ ! -f ".railway/config.json" ]; then
    echo "🆕 Initializing new Railway project..."
    railway init
fi

# Add Redis if not exists
echo "📦 Setting up Redis..."
railway add --database redis || echo "Redis might already exist"

# Add PostgreSQL if not exists
echo "🗍 Setting up PostgreSQL..."
railway add --database postgresql || echo "PostgreSQL might already exist"

# Deploy Master service
echo "🤖 Deploying Master Orchestrator..."
railway add --service --name master || echo "Master service might already exist"
railway up --service master

# Deploy Worker service
echo "👷 Deploying Worker template..."
railway add --service --name worker || echo "Worker service might already exist"
railway up --service worker

# Deploy UI service
echo "🎨 Deploying UI..."
railway add --service --name ui || echo "UI service might already exist"
railway up --service ui

# Get project info
echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 Your Railway project:"
railway status

echo ""
echo "🎯 Next steps:"
echo "1. Set your environment variables in the Railway dashboard"
echo "2. Build and push the Docker image:"
echo "   docker build -f Dockerfile.worker -t ghcr.io/$GITHUB_USERNAME/crew-worker:latest ."
echo "   docker push ghcr.io/$GITHUB_USERNAME/crew-worker:latest"
echo "3. Configure the worker service to use your Docker image"
echo "4. Access your UI at the generated Railway domain"
echo ""
echo "Happy orchestrating! 🎆"