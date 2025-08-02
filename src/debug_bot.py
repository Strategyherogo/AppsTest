#!/usr/bin/env python3
"""
Debug version with extensive logging
"""

import os
import logging
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# Log ALL events
@app.middleware
def log_request(logger, body, next):
    logger.debug(f"Received event: {json.dumps(body, indent=2)}")
    return next()

@app.event("app_mention")
def handle_app_mention(event, say, ack, logger):
    """Handle app mentions"""
    ack()
    logger.info(f"APP MENTION RECEIVED!")
    logger.info(f"User: {event['user']}")
    logger.info(f"Text: {event['text']}")
    logger.info(f"Channel: {event['channel']}")
    
    try:
        response = say(f"Hello <@{event['user']}>! I heard you!")
        logger.info(f"Response sent: {response}")
    except Exception as e:
        logger.error(f"Failed to send response: {e}")

@app.event("message")
def handle_message(event, logger):
    """Handle messages"""
    if event.get('subtype') is None:
        logger.info(f"Regular message: {event.get('text', '')[:50]}...")

# Handle socket mode connections
@app.event("hello")
def handle_hello(event, logger):
    logger.info("Connected to Slack!")

if __name__ == "__main__":
    try:
        print("🔍 Debug Bot Starting...")
        print(f"Bot Token: {os.getenv('SLACK_BOT_TOKEN')[:20]}...")
        print(f"App Token: {os.getenv('SLACK_APP_TOKEN')[:20]}...")
        
        handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
        print("\n⚡️ Debug bot is running!")
        print("Try: @Claude Assistant Test hello")
        print("\nWatching for ALL events...")
        handler.start()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()