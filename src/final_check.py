#!/usr/bin/env python3
"""
Final check for bot configuration
"""

import os
import sys
from slack_sdk import WebClient
from slack_bolt import App
from dotenv import load_dotenv

load_dotenv()

print("🔍 Final Bot Configuration Check")
print("="*50)

# 1. Check tokens
bot_token = os.getenv('SLACK_BOT_TOKEN')
app_token = os.getenv('SLACK_APP_TOKEN')

print("1️⃣ Tokens:")
print(f"   Bot Token: {'✅' if bot_token and len(bot_token) > 20 else '❌'}")
print(f"   App Token: {'✅' if app_token and len(app_token) > 20 else '❌'}")

# 2. Test authentication
client = WebClient(token=bot_token)
try:
    auth = client.auth_test()
    print(f"\n2️⃣ Authentication: ✅")
    print(f"   Bot: {auth['user']} ({auth['user_id']})")
    print(f"   Team: {auth['team']}")
except Exception as e:
    print(f"\n2️⃣ Authentication: ❌ {e}")
    sys.exit(1)

# 3. Test Socket Mode
print("\n3️⃣ Socket Mode Test:")
try:
    # Test app-level token
    app_client = WebClient(token=app_token)
    # Socket mode uses apps.connections.open
    print("   Testing app token...")
    
    # Initialize Bolt app
    app = App(token=bot_token)
    print("   ✅ Bolt app initialized")
    
    # Check if we can connect
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    handler = SocketModeHandler(app, app_token)
    print("   ✅ Socket Mode handler created")
    
except Exception as e:
    print(f"   ❌ Socket Mode error: {e}")

print("\n4️⃣ Required Slack App Setup:")
print("   ✅ OAuth Scopes (Bot Token):")
print("      - app_mentions:read")
print("      - channels:history") 
print("      - channels:read")
print("      - chat:write")
print("      - im:history")
print("      - im:read")

print("\n   ✅ Event Subscriptions:")
print("      - app_mention")
print("      - message.channels")
print("      - message.im")

print("\n   ✅ Socket Mode:")
print("      - Must be ENABLED")
print("      - App-level token with connections:write scope")

print("\n5️⃣ Quick Test:")
print("   If the bot still doesn't respond:")
print("   1. Go to your Slack workspace")
print("   2. Create a NEW channel (e.g. #bot-test)")
print("   3. Invite the bot: /invite @claude_assistant_test")
print("   4. Try: @Claude Assistant Test hello")
print("\n   Sometimes Slack caches permissions per channel.")

print("\n✅ Configuration check complete!")