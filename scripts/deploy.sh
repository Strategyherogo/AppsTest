#!/bin/bash

# Deployment script for Slack Task Bot

set -e

echo "🚀 Deploying Slack Task Bot..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your credentials"
    exit 1
fi

# Validate required environment variables
required_vars=("SLACK_BOT_TOKEN" "SLACK_APP_TOKEN" "SLACK_SIGNING_SECRET" "OPENAI_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf '%s\n' "${missing_vars[@]}"
    exit 1
fi

# Docker deployment
if command -v docker &> /dev/null; then
    echo "📦 Building Docker image..."
    docker-compose build
    
    echo "🔄 Starting services..."
    docker-compose up -d
    
    echo "✅ Bot deployed successfully!"
    echo "View logs: docker-compose logs -f slack-bot"
else
    # Local deployment
    echo "🐍 Setting up Python environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "🤖 Starting bot..."
    python src/slack_bot.py
fi