#!/bin/bash
# VM Setup Script for Slack Mention Tracker Bot
# Works on Ubuntu/Debian VMs (AWS EC2, DigitalOcean, Vultr, etc.)

echo "🚀 Setting up Slack Mention Tracker Bot..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv git

# Install process manager
echo "📊 Installing PM2 for process management..."
curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pm2

# Clone repository (replace with your repo)
echo "📥 Cloning repository..."
if [ ! -d "slack-mention-tracker" ]; then
    git clone https://github.com/YOUR_USERNAME/slack-mention-tracker.git
fi
cd slack-mention-tracker

# Create virtual environment
echo "🔧 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo "🔐 Creating .env file..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Slack Configuration
SLACK_BOT_TOKEN=your-bot-token-here
SLACK_APP_TOKEN=your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here

# App Configuration
USE_SIMPLE_ANALYZER=True
DEBUG=False
LOG_LEVEL=INFO
EOF
    echo "⚠️  Please edit .env file with your actual credentials!"
fi

# Create PM2 ecosystem file
echo "⚙️ Creating PM2 configuration..."
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'slack-bot',
    script: 'venv/bin/python',
    args: 'src/mention_tracker.py',
    cwd: '/home/$USER/slack-mention-tracker',
    interpreter: '/bin/bash',
    interpreter_args: '-c',
    env: {
      PATH: '/home/$USER/slack-mention-tracker/venv/bin:' + process.env.PATH
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

# Setup PM2 startup
echo "🔄 Setting up auto-start on boot..."
pm2 startup systemd -u $USER --hp /home/$USER
pm2 save

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Slack credentials:"
echo "   nano .env"
echo ""
echo "2. Start the bot:"
echo "   pm2 start ecosystem.config.js"
echo ""
echo "3. View logs:"
echo "   pm2 logs slack-bot"
echo ""
echo "4. Bot will auto-start on system reboot"
echo ""
echo "🎯 Useful PM2 commands:"
echo "   pm2 status          - Check bot status"
echo "   pm2 restart slack-bot - Restart bot"
echo "   pm2 stop slack-bot    - Stop bot"
echo "   pm2 monit           - Monitor in real-time"