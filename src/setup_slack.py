#!/usr/bin/env python3
"""
Slack Bot Setup Helper
Helps verify credentials and provides setup instructions
"""

import os
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

def test_slack_connection():
    """Test Slack API connection and credentials"""
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    app_token = os.getenv('SLACK_APP_TOKEN')
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
    
    print("🔍 Checking Slack Configuration...")
    print("="*50)
    
    # Check if credentials exist
    if not bot_token or bot_token == 'xoxb-your-bot-token':
        print("❌ Bot token not configured")
        return False
    
    if not app_token or app_token == 'xapp-your-app-token':
        print("❌ App token not configured")
        return False
        
    if not signing_secret or signing_secret == 'your-signing-secret':
        print("❌ Signing secret not configured")
        return False
    
    print("✅ Credentials found in .env file")
    
    # Test bot token
    print("\n🔑 Testing Bot Token...")
    client = WebClient(token=bot_token)
    
    try:
        response = client.auth_test()
        print(f"✅ Bot authenticated successfully!")
        print(f"   Team: {response['team']}")
        print(f"   Bot User: {response['user']}")
        print(f"   Bot ID: {response['user_id']}")
    except SlackApiError as e:
        print(f"❌ Bot token invalid: {e.response['error']}")
        print("\n🔧 How to fix:")
        print("1. Go to https://api.slack.com/apps")
        print("2. Select your app")
        print("3. Go to 'OAuth & Permissions'")
        print("4. Click 'Reinstall to Workspace'")
        print("5. Copy the new Bot User OAuth Token")
        return False
    
    return True

def provide_setup_instructions():
    """Provide detailed setup instructions"""
    print("\n📋 Slack App Setup Instructions")
    print("="*50)
    print("""
1. Create a Slack App:
   - Go to https://api.slack.com/apps
   - Click 'Create New App' > 'From scratch'
   - Name your app (e.g., 'Task Bot')
   - Select your workspace

2. Configure Bot Token Scopes:
   - Go to 'OAuth & Permissions'
   - Add these Bot Token Scopes:
     • channels:history
     • channels:read
     • chat:write
     • im:history
     • im:read
     • users:read
     • reactions:write
     • reactions:read
   - Click 'Install to Workspace'
   - Copy the Bot User OAuth Token

3. Enable Socket Mode:
   - Go to 'Socket Mode' in the sidebar
   - Enable Socket Mode
   - Click 'Generate' to create an app-level token
   - Add scope: connections:write
   - Copy the App-Level Token

4. Subscribe to Events:
   - Go to 'Event Subscriptions'
   - Enable Events
   - Add these bot events:
     • message.channels
     • message.im
     • app_mention
   - Save changes

5. Get Signing Secret:
   - Go to 'Basic Information'
   - Copy the Signing Secret

6. Update your .env file with all three values

7. Reinstall the app if needed:
   - Go to 'OAuth & Permissions'
   - Click 'Reinstall to Workspace'
""")

def check_openai():
    """Check OpenAI configuration"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    print("\n🤖 Checking OpenAI Configuration...")
    print("="*50)
    
    if not api_key or api_key == 'your-openai-api-key':
        print("❌ OpenAI API key not configured")
        print("\n🔧 How to get an OpenAI API key:")
        print("1. Go to https://platform.openai.com/api-keys")
        print("2. Create a new API key")
        print("3. Add it to your .env file")
        return False
    
    print("✅ OpenAI API key configured")
    return True

def main():
    print("🤖 Slack Task Bot Setup Helper")
    print("="*50)
    
    # Test Slack connection
    slack_ok = test_slack_connection()
    
    # Check OpenAI
    openai_ok = check_openai()
    
    if not slack_ok:
        provide_setup_instructions()
    
    if slack_ok and openai_ok:
        print("\n✅ All systems ready!")
        print("You can now run: python src/slack_bot.py")
    else:
        print("\n❌ Setup incomplete - please follow the instructions above")

if __name__ == "__main__":
    main()