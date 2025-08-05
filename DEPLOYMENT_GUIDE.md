# Slack Task Bot Deployment Guide

## Overview
This guide will help you deploy the Slack Task Bot to DigitalOcean. The bot tracks mentions of @Evgeny and creates task lists from those mentions.

## Prerequisites
- DigitalOcean droplet (Ubuntu 20.04 or newer)
- SSH access to the droplet
- GitHub repository with your bot code

## Deployment Steps

### 1. Connect to Your Droplet
```bash
ssh root@your-droplet-ip
```

### 2. Prepare Credentials
Before running the setup, you need to configure your Slack credentials. The setup script uses placeholder values that you'll need to replace.

```bash
# Download the setup script
wget https://raw.githubusercontent.com/Strategyherogo/AppsTest/main/setup_droplet.sh

# Make it executable
chmod +x setup_droplet.sh

# Edit the script to add your credentials
nano setup_droplet.sh
```

Find these lines and replace with your actual values:
- `SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN_HERE`
- `SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN_HERE`
- `SLACK_SIGNING_SECRET=YOUR_SLACK_SIGNING_SECRET_HERE`

### 3. Run Setup Script
After adding your credentials, run the setup:

```bash
./setup_droplet.sh
```

This script will:
- Install Python 3, Node.js, and PM2
- Clone your repository
- Set up a Python virtual environment
- Install dependencies
- Configure environment variables
- Start the bot with PM2

### 4. Verify Deployment
After setup completes, verify the bot is running:

```bash
# Check PM2 status
pm2 status

# View logs
pm2 logs slack-bot

# View last 50 lines of logs
pm2 logs slack-bot --lines 50
```

### 5. Test the Bot
1. Go to your Slack workspace
2. Find a channel where the bot is a member
3. Mention @Evgeny in a message
4. Check the logs to see if the mention was tracked

## Troubleshooting

### If the Bot Isn't Running
Run the fix script:

```bash
cd ~/slack-mention-tracker
./fix_bot.sh
```

### Common Issues

1. **Bot not seeing messages**
   - Ensure the bot is invited to channels
   - Check that the bot has required scopes: `app_mentions:read`, `channels:history`, `chat:write`

2. **Python version issues**
   - The bot requires Python 3.8+
   - Don't use Python 3.13 with pydantic

3. **Missing environment variables**
   - Check `.env` file exists
   - Verify all tokens are correct

## PM2 Commands

```bash
# Start bot
pm2 start slack-bot

# Stop bot
pm2 stop slack-bot

# Restart bot
pm2 restart slack-bot

# View real-time logs
pm2 logs slack-bot

# Delete from PM2
pm2 delete slack-bot

# Save PM2 config
pm2 save

# List all processes
pm2 list
```

## Updating the Bot

To update the bot code:

```bash
cd ~/slack-mention-tracker
git pull
pm2 restart slack-bot
```

## Configuration

The bot uses these environment variables (stored in `.env`):

- `SLACK_BOT_TOKEN`: Bot user OAuth token (xoxb-...)
- `SLACK_APP_TOKEN`: App-level token for Socket Mode (xapp-...)
- `SLACK_SIGNING_SECRET`: Signing secret for request verification
- `USE_SIMPLE_ANALYZER`: Set to True for keyword-based task detection

## Bot Features

- **Auto-tracks**: User ID 'U04NYQN6NEM' (Evgeny Goncharov)
- **Commands** (mention the bot):
  - `track me` - Start tracking your mentions
  - `my mentions` - See recent mentions
  - `my tasks` - See task-like mentions
  - `clear mentions` - Clear mention history
  - `stop tracking` - Stop tracking
  - `help` - Show help

## Security Notes

- Keep your tokens secret
- Use environment variables, never hardcode tokens
- Regularly rotate tokens if needed
- Monitor bot activity through logs

## Support

If you encounter issues:
1. Check PM2 logs: `pm2 logs slack-bot`
2. Verify environment variables in `.env`
3. Ensure bot has correct Slack permissions
4. Check network connectivity

## Next Steps

After successful deployment:
1. Invite the bot to relevant channels
2. Test mention tracking
3. Configure any additional settings
4. Monitor logs for errors