#!/bin/bash
# Complete fix script for Slack bot on DigitalOcean droplet

echo "🔧 Starting complete fix for Slack bot..."

# Navigate to project directory
cd ~/slack-mention-tracker || {
    echo "❌ Project directory not found! Please clone the repo first."
    exit 1
}

# Stop any running bot instances
echo "⏹️  Stopping any running instances..."
pm2 stop slack-bot 2>/dev/null || true
pm2 delete slack-bot 2>/dev/null || true

# Clean up old virtual environment
echo "🧹 Cleaning up old environment..."
rm -rf venv
rm -f requirements.txt

# Create fresh virtual environment
echo "🐍 Creating fresh Python environment..."
python3 -m venv venv
source venv/bin/activate

# Create clean requirements.txt without pydantic
echo "📝 Creating clean requirements.txt..."
cat > requirements.txt << 'EOF'
slack-sdk==3.31.0
slack-bolt==1.19.1
python-dotenv==1.0.1
aiohttp==3.9.5
requests==2.31.0
EOF

# Upgrade pip and install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Creating .env file..."
    cat > .env << 'EOF'
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN_HERE
SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN_HERE
SLACK_SIGNING_SECRET=YOUR_SLACK_SIGNING_SECRET_HERE
USE_SIMPLE_ANALYZER=True
EOF
fi

# Create PM2 ecosystem file
echo "⚙️  Creating PM2 configuration..."
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'slack-bot',
    script: 'venv/bin/python',
    args: 'src/mention_tracker.py',
    cwd: process.cwd(),
    interpreter: '/bin/bash',
    interpreter_args: '-c',
    env: {
      PATH: process.cwd() + '/venv/bin:' + process.env.PATH
    },
    error_file: 'logs/pm2-error.log',
    out_file: 'logs/pm2-out.log',
    log_file: 'logs/pm2-combined.log',
    time: true,
    restart_delay: 5000,
    max_restarts: 10,
    autorestart: true
  }]
}
EOF

# Create logs directory
mkdir -p logs

# Create src directory if it doesn't exist
mkdir -p src

# Download the bot files if they don't exist
if [ ! -f src/mention_tracker.py ] || [ ! -f src/simple_analyzer.py ] || [ ! -f src/config.py ]; then
    echo "📥 Downloading bot files from GitHub..."
    # Clone just the files we need
    if [ ! -f src/mention_tracker.py ]; then
        wget -q https://raw.githubusercontent.com/Strategyherogo/AppsTest/main/src/mention_tracker.py -O src/mention_tracker.py
    fi
    if [ ! -f src/simple_analyzer.py ]; then
        wget -q https://raw.githubusercontent.com/Strategyherogo/AppsTest/main/src/simple_analyzer.py -O src/simple_analyzer.py
    fi
    if [ ! -f src/config.py ]; then
        wget -q https://raw.githubusercontent.com/Strategyherogo/AppsTest/main/src/config.py -O src/config.py
    fi
fi

# Start the bot with PM2
echo "🚀 Starting bot with PM2..."
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Show status and logs
echo "✅ Setup complete! Bot is starting..."
echo ""
echo "📊 Bot status:"
pm2 status
echo ""
echo "📜 Recent logs:"
pm2 logs slack-bot --lines 20 --nostream

echo ""
echo "🎯 Useful commands:"
echo "  pm2 logs slack-bot     - View real-time logs"
echo "  pm2 status             - Check bot status"
echo "  pm2 restart slack-bot  - Restart bot"
echo "  pm2 stop slack-bot     - Stop bot"
echo ""
echo "✨ Your bot should now be running and tracking mentions!"