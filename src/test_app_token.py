#!/usr/bin/env python3
"""Test Slack app token"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

def test_app_token():
    app_token = os.getenv('SLACK_APP_TOKEN')
    
    print(f"App Token: {app_token[:20]}...{app_token[-20:]}")
    
    # Test app token
    client = WebClient(token=app_token)
    
    try:
        # App tokens use apps.connections.open
        response = client.api_call(
            "apps.connections.open",
            http_verb="POST",
            headers={"Authorization": f"Bearer {app_token}"}
        )
        print("✅ App token is valid!")
        print(f"Response: {response}")
    except SlackApiError as e:
        print(f"❌ App token error: {e.response['error']}")
        print("\nTo fix:")
        print("1. Go to https://api.slack.com/apps")
        print("2. Select your app")
        print("3. Go to 'Socket Mode' in sidebar")
        print("4. Enable Socket Mode")
        print("5. Click 'Generate' for app-level token")
        print("6. Add scope: connections:write")
        print("7. Copy the new token (starts with xapp-)")

if __name__ == "__main__":
    test_app_token()