# DigitalOcean App Platform Deployment

## Quick Deploy to App Platform

### Option 1: Deploy to Existing App

If you already have an app on DigitalOcean App Platform:

1. **Update your app's GitHub repo** to point to `Strategyherogo/AppsTest`
2. **Set environment variables** in App Platform:
   ```
   SLACK_BOT_TOKEN = (your bot token)
   SLACK_APP_TOKEN = (your app token)
   SLACK_SIGNING_SECRET = (your signing secret)
   USE_SIMPLE_ANALYZER = True
   ```
3. **Deploy** - App Platform will automatically redeploy

### Option 2: Create New App

1. Go to DigitalOcean App Platform
2. Click "Create App"
3. Choose GitHub and select `Strategyherogo/AppsTest` repository
4. Use these settings:
   - **Type**: Worker (not Web Service)
   - **Run Command**: `python src/mention_tracker.py`
   - **Instance Size**: Basic ($5-12/month)
   - **Region**: Choose closest to you

5. Add environment variables:
   - `SLACK_BOT_TOKEN` (mark as secret)
   - `SLACK_APP_TOKEN` (mark as secret)  
   - `SLACK_SIGNING_SECRET` (mark as secret)
   - `USE_SIMPLE_ANALYZER` = `True`

### Option 3: Use app.yaml

```bash
doctl apps create --spec app.yaml
```

Then update the app with your credentials:
```bash
doctl apps update YOUR-APP-ID --env SLACK_BOT_TOKEN=your-token
doctl apps update YOUR-APP-ID --env SLACK_APP_TOKEN=your-token
doctl apps update YOUR-APP-ID --env SLACK_SIGNING_SECRET=your-secret
```

## Important Notes

- The bot uses Socket Mode which maintains a persistent connection
- App Platform may restart the bot occasionally (this is normal)
- Check logs in App Platform dashboard for any issues
- The bot will auto-reconnect if connection drops

## Monitoring

In App Platform dashboard:
- View **Runtime Logs** to see bot activity
- Check **Build Logs** if deployment fails
- Monitor **Insights** for resource usage

## Troubleshooting

If the bot isn't working:
1. Check environment variables are set correctly
2. Verify the bot has been invited to Slack channels
3. Look at Runtime Logs for error messages
4. Ensure you're using the `worker` process type, not `web`