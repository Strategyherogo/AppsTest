# Deployment Guide for Slack Mention Tracker Bot

The bot uses Socket Mode, so it doesn't need a public URL. You just need a server that can run Python continuously.

## Option 1: Railway (Recommended - Easy)

1. **Sign up** at [railway.app](https://railway.app)

2. **Install Railway CLI**:
   ```bash
   brew install railway
   ```

3. **Deploy**:
   ```bash
   railway login
   railway link
   railway up
   ```

4. **Add environment variables** in Railway dashboard:
   - `SLACK_BOT_TOKEN`
   - `SLACK_APP_TOKEN`
   - `SLACK_SIGNING_SECRET`
   - `USE_SIMPLE_ANALYZER=True`

5. **Deploy**: Railway will auto-deploy from GitHub

## Option 2: Render

1. **Sign up** at [render.com](https://render.com)

2. **Connect GitHub** repository

3. **Create new service**:
   - Type: Background Worker
   - Runtime: Python
   - Build: `pip install -r requirements.txt`
   - Start: `python src/mention_tracker.py`

4. **Add environment variables** in Render dashboard

## Option 3: Heroku

1. **Create** `runtime.txt`:
   ```
   python-3.9.19
   ```

2. **Deploy**:
   ```bash
   heroku create your-bot-name
   heroku config:set SLACK_BOT_TOKEN=xoxb-...
   heroku config:set SLACK_APP_TOKEN=xapp-...
   heroku config:set SLACK_SIGNING_SECRET=...
   git push heroku main
   heroku ps:scale worker=1
   ```

## Option 4: VPS (DigitalOcean, Linode, etc.)

1. **SSH to server** and clone repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/slack-mention-tracker.git
   cd slack-mention-tracker
   ```

2. **Setup Python**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create `.env`** file with your credentials

4. **Use systemd** for auto-restart:
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

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start service**:
   ```bash
   sudo systemctl enable slack-bot
   sudo systemctl start slack-bot
   ```

## Option 5: Docker (Any Cloud)

1. **Build and push** to Docker Hub:
   ```bash
   docker build -t yourusername/slack-bot .
   docker push yourusername/slack-bot
   ```

2. **Run anywhere**:
   ```bash
   docker run -d \
     -e SLACK_BOT_TOKEN=xoxb-... \
     -e SLACK_APP_TOKEN=xapp-... \
     -e SLACK_SIGNING_SECRET=... \
     --restart always \
     yourusername/slack-bot
   ```

## Free Options

- **Railway**: Free tier with $5 credit/month
- **Render**: Free tier (spins down after 15 min inactivity)
- **Fly.io**: Free tier with 3 small VMs
- **GitHub Codespaces**: Can run bot during development

## Important Notes

1. The bot uses **Socket Mode** - no webhooks needed
2. It must run **continuously** to track mentions
3. All credentials go in **environment variables**, never commit `.env`
4. The bot will auto-reconnect if disconnected

## Monitoring

Add health checks by modifying the bot to ping a service like:
- UptimeRobot
- Healthchecks.io
- Better Stack

## Quick Start (Railway)

```bash
# From your repo directory
railway login
railway link  # Create new project
railway up    # Deploy

# Then add env vars in Railway dashboard
```

The bot will start tracking mentions immediately after deployment!