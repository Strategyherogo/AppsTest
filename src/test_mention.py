#!/usr/bin/env python3
"""
Simple test for app mentions
"""

import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

@app.event("app_mention")
def handle_app_mention(event, say, logger):
    """Handle app mentions"""
    logger.info(f"App mention received: {event}")
    
    user = event['user']
    text = event['text']
    
    # Simple response
    say(f"Hello <@{user}>! You said: {text}")
    
    # Also try a block message
    say(blocks=[{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"👋 Hi <@{user}>! I received your message:\n> {text}"
        }
    }])

@app.event("message")
def handle_message(event, logger):
    """Log all messages for debugging"""
    logger.info(f"Message event: {event}")

# Catch-all for other events
@app.event("message")
def handle_message_events(body, logger):
    logger.info(f"Received message event: {body}")

if __name__ == "__main__":
    try:
        handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
        print("⚡️ Simple mention test bot is running!")
        print("Try mentioning the bot in Slack: @Claude Assistant Test hello")
        handler.start()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. Your app has Socket Mode enabled")
        print("2. Event Subscriptions are enabled")
        print("3. 'app_mention' event is subscribed")
        print("4. Bot is in the channel")