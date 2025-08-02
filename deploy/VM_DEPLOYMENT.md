# VM Deployment Guide

Deploy the Slack bot on any Linux VM (AWS EC2, DigitalOcean, Google Cloud, Azure, etc.)

## Quick Start (5 minutes)

### 1. Create a VM

**DigitalOcean** (Simplest):
```bash
# $6/month droplet is enough
- Ubuntu 22.04
- Basic ($6/month)
- Any region
```

**AWS EC2**:
```bash
# t2.micro (free tier)
- Ubuntu 22.04 LTS
- t2.micro
- Allow SSH (port 22)
```

### 2. Connect to VM
```bash
ssh root@your-vm-ip  # DigitalOcean
# or
ssh -i your-key.pem ubuntu@your-vm-ip  # AWS
```

### 3. Run Setup Script
```bash
# Download and run setup script
wget https://raw.githubusercontent.com/YOUR_USERNAME/slack-mention-tracker/main/deploy/vm-setup.sh
chmod +x vm-setup.sh
./vm-setup.sh
```

### 4. Configure Credentials
```bash
cd slack-mention-tracker
nano .env
```

Add your credentials:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
```

### 5. Start Bot
```bash
pm2 start ecosystem.config.js
pm2 logs slack-bot  # View logs
```

## Manual Setup

### 1. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3 python3-pip python3-venv git

# Install Node.js and PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

### 2. Clone and Setup
```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/slack-mention-tracker.git
cd slack-mention-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure
```bash
# Copy example env
cp .env.example .env
nano .env  # Add your tokens
```

### 4. Run with PM2
```bash
# Start bot
pm2 start venv/bin/python --name slack-bot -- src/mention_tracker.py

# Save PM2 config
pm2 save
pm2 startup  # Follow instructions to enable auto-start
```

## Using Systemd (Alternative to PM2)

### 1. Create Service File
```bash
sudo nano /etc/systemd/system/slack-bot.service
```

```ini
[Unit]
Description=Slack Mention Tracker Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/slack-mention-tracker
Environment="PATH=/home/ubuntu/slack-mention-tracker/venv/bin"
ExecStart=/home/ubuntu/slack-mention-tracker/venv/bin/python src/mention_tracker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable slack-bot
sudo systemctl start slack-bot
sudo systemctl status slack-bot
```

## VM Providers Comparison

| Provider | Cost | Free Tier | Setup Ease |
|----------|------|-----------|------------|
| DigitalOcean | $6/month | $200 credit | ⭐⭐⭐⭐⭐ |
| AWS EC2 | ~$5/month | 1 year t2.micro | ⭐⭐⭐ |
| Google Cloud | ~$5/month | $300 credit | ⭐⭐⭐ |
| Vultr | $6/month | Sometimes | ⭐⭐⭐⭐ |
| Linode | $5/month | $100 credit | ⭐⭐⭐⭐ |
| Oracle Cloud | Free | Always free tier | ⭐⭐ |

## Monitoring

### Check Status
```bash
# PM2
pm2 status
pm2 logs slack-bot

# Systemd
sudo systemctl status slack-bot
sudo journalctl -u slack-bot -f
```

### Set Up Monitoring
```bash
# Install monitoring
pm2 install pm2-logrotate  # Rotate logs
pm2 set pm2-logrotate:max_size 10M

# Web monitoring
pm2 web  # Opens web dashboard on port 9615
```

## Security

### 1. Firewall
```bash
# Only SSH needed (no web ports)
sudo ufw allow OpenSSH
sudo ufw enable
```

### 2. Updates
```bash
# Auto security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 3. Non-root User
```bash
# Create user
sudo adduser slackbot
sudo usermod -aG sudo slackbot

# Switch to user
su - slackbot
```

## Backup

### Bot State
The bot stores mentions in memory. To persist:
```bash
# Add Redis (optional)
sudo apt install redis-server
# Update code to use Redis for persistence
```

### Credentials
```bash
# Backup .env file
cp .env .env.backup
```

## Troubleshooting

### Bot Won't Start
```bash
# Check logs
pm2 logs slack-bot --lines 50

# Test manually
cd slack-mention-tracker
source venv/bin/activate
python src/mention_tracker.py
```

### Connection Issues
```bash
# Check network
curl -I https://slack.com

# Restart
pm2 restart slack-bot
```

### Memory Issues
```bash
# Check resources
free -h
df -h

# Restart daily (cron)
crontab -e
# Add: 0 4 * * * pm2 restart slack-bot
```

## Cost Optimization

**Free Options:**
- Oracle Cloud: Always free tier
- Google Cloud: $300 credit
- AWS: 12 months free t2.micro

**Cheapest Paid:**
- Vultr/Linode: $5/month
- DigitalOcean: $6/month with better UI

The bot uses minimal resources - 512MB RAM is enough!