#!/usr/bin/env python3
"""
Diagnose Slack bot configuration
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

def diagnose():
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    app_token = os.getenv('SLACK_APP_TOKEN')
    
    print("🔍 Slack Bot Diagnostic")
    print("="*50)
    
    client = WebClient(token=bot_token)
    
    # 1. Check bot info
    try:
        auth_info = client.auth_test()
        bot_id = auth_info['user_id']
        print(f"✅ Bot authenticated: {auth_info['user']} ({bot_id})")
        print(f"   Team: {auth_info['team']}")
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        return
    
    # 2. Check OAuth scopes
    print("\n📋 OAuth Scopes:")
    try:
        # Get bot scopes
        response = client.api_call("auth.test")
        print("   Bot has access (auth.test passed)")
        
        # Try to list channels to check permissions
        try:
            channels = client.conversations_list(limit=1)
            print("   ✅ channels:read - Can list channels")
        except:
            print("   ❌ channels:read - Cannot list channels")
        
        # Try to check if we can write
        print("\n   Checking write permissions...")
        # We'll check this by looking at bot info
        
    except Exception as e:
        print(f"   Error checking scopes: {e}")
    
    # 3. Check app configuration
    print("\n🔧 App Configuration:")
    print(f"   App Token present: {'✅' if app_token and len(app_token) > 20 else '❌'}")
    
    # 4. List channels bot is in
    print("\n📍 Channels bot is member of:")
    try:
        result = client.conversations_list(
            types="public_channel,private_channel",
            limit=100
        )
        
        bot_channels = []
        for channel in result['channels']:
            if channel.get('is_member', False):
                bot_channels.append(channel)
                print(f"   ✅ #{channel['name']} (ID: {channel['id']})")
        
        if not bot_channels:
            print("   ❌ Bot is not a member of any channels!")
            print("   Fix: Invite the bot with /invite @claude_assistant_test")
    except Exception as e:
        print(f"   Error listing channels: {e}")
    
    # 5. Check if bot can send messages
    print("\n💬 Testing message sending:")
    if bot_channels:
        test_channel = bot_channels[0]
        try:
            response = client.chat_postMessage(
                channel=test_channel['id'],
                text="🔧 Diagnostic test message - Bot can send messages!"
            )
            print(f"   ✅ Successfully sent test message to #{test_channel['name']}")
        except SlackApiError as e:
            print(f"   ❌ Cannot send messages: {e.response['error']}")
            if e.response['error'] == 'missing_scope':
                print("   Fix: Add 'chat:write' scope to your bot")
    
    # 6. Check required event subscriptions
    print("\n📡 Required Event Subscriptions:")
    print("   Make sure these are enabled in your Slack app:")
    print("   - app_mention")
    print("   - message.channels")
    print("   - message.im")
    
    print("\n🔍 Required OAuth Scopes:")
    print("   Bot Token Scopes needed:")
    print("   - app_mentions:read")
    print("   - channels:history")
    print("   - channels:read")
    print("   - chat:write")
    print("   - im:history")
    print("   - im:read")
    
    print("\n✅ Diagnostic complete!")

if __name__ == "__main__":
    diagnose()