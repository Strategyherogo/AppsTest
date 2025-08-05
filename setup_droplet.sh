#!/bin/bash
# Setup script for fresh DigitalOcean droplet

echo "🚀 Setting up Slack bot from scratch..."

# Update system first
echo "📦 Updating system..."
apt update && apt upgrade -y

# Install required packages
echo "🔧 Installing Python and Git..."
apt install -y python3 python3-pip python3-venv git nodejs npm

# Install PM2
echo "📊 Installing PM2..."
npm install -g pm2

# Clone your repository
echo "📥 Cloning your repository..."
cd ~
git clone https://github.com/Strategyherogo/AppsTest.git slack-mention-tracker
cd slack-mention-tracker

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Create clean requirements.txt
echo "📝 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
slack-sdk==3.31.0
slack-bolt==1.19.1
python-dotenv==1.0.1
aiohttp==3.9.5
requests==2.31.0
EOF

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo "🔐 Creating .env file..."
cat > .env << 'EOF'
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN_HERE
SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN_HERE
SLACK_SIGNING_SECRET=YOUR_SLACK_SIGNING_SECRET_HERE
USE_SIMPLE_ANALYZER=True
EOF

# Create PM2 config
echo "⚙️ Creating PM2 configuration..."
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'slack-bot',
    script: 'venv/bin/python',
    args: 'src/mention_tracker.py',
    cwd: '/root/slack-mention-tracker',
    interpreter: '/bin/bash',
    interpreter_args: '-c',
    env: {
      PATH: '/root/slack-mention-tracker/venv/bin:' + process.env.PATH
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
    echo "📥 Downloading bot files from repository..."
    # You'll need to copy these files manually or ensure they're in the git repo
    echo "⚠️  Please ensure all source files are in the src/ directory:"
    echo "   - src/mention_tracker.py"
    echo "   - src/simple_analyzer.py"
    echo "   - src/config.py"
fi

# Start bot
echo "🚀 Starting bot..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u root --hp /root

echo "✅ Setup complete!"
echo ""
pm2 status
echo ""
echo "📜 View logs: pm2 logs slack-bot"
echo "🔄 Restart: pm2 restart slack-bot"