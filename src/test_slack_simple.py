#!/usr/bin/env python3
"""
Test Slack connection and basic functionality
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from simple_analyzer import SimpleMessageAnalyzer

load_dotenv()

def test_bot():
    """Test bot functionality"""
    
    # Initialize Slack client
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    client = WebClient(token=bot_token)
    
    print("🤖 Testing Slack Task Bot")
    print("="*50)
    
    # Test authentication
    try:
        auth_response = client.auth_test()
        print(f"✅ Bot authenticated as: {auth_response['user']}")
        print(f"   Team: {auth_response['team']}")
        print(f"   Bot ID: {auth_response['user_id']}")
    except SlackApiError as e:
        print(f"❌ Authentication failed: {e.response['error']}")
        return
    
    # Initialize analyzer
    print("\n🔍 Initializing task analyzer...")
    analyzer = SimpleMessageAnalyzer()
    
    # Test messages
    test_messages = [
        "Remember to send the report to the client by Friday",
        "Can we schedule a meeting tomorrow at 2pm?",
        "Just finished the presentation",
        "Please review the pull request when you get a chance",
        "Don't forget to update the documentation today"
    ]
    
    print("\n📝 Testing task detection:")
    print("-"*50)
    
    for msg in test_messages:
        result = analyzer.analyze_message(msg)
        print(f"\nMessage: '{msg}'")
        print(f"Is Task: {result['is_task']} (confidence: {result['confidence']:.1%})")
        
        if result['is_task'] and result['task_details']:
            details = result['task_details']
            print(f"  Title: {details['title']}")
            print(f"  Priority: {details['priority']}")
            print(f"  Due: {details.get('due_date', 'Not specified')}")
    
    # Try to send a test message
    print("\n\n💬 Attempting to send a test message...")
    try:
        # Get list of channels
        channels_response = client.conversations_list(
            types="public_channel,private_channel",
            limit=10
        )
        
        if channels_response['channels']:
            # Find a suitable channel
            test_channel = None
            for channel in channels_response['channels']:
                if channel['is_member']:
                    test_channel = channel
                    break
            
            if test_channel:
                print(f"✅ Found channel: #{test_channel['name']}")
                
                # Send a test message
                response = client.chat_postMessage(
                    channel=test_channel['id'],
                    text="🤖 Task Bot is online! I'll help you detect and manage tasks in your messages.",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "🤖 *Task Bot is online!*\n\nI'll help you detect and manage tasks in your messages."
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Available commands:*\n• `@claude_assistant_test help` - Show help\n• `@claude_assistant_test analyze [message]` - Analyze a message for tasks\n• `@claude_assistant_test settings` - Configure your preferences"
                            }
                        }
                    ]
                )
                print(f"✅ Test message sent to #{test_channel['name']}")
            else:
                print("❌ No channels found where bot is a member")
        
    except SlackApiError as e:
        print(f"❌ Failed to send message: {e.response['error']}")
        print("   Make sure the bot has been invited to a channel!")
    
    print("\n\n✅ Test completed!")
    print("\n📌 Next steps:")
    print("1. Invite the bot to a channel: /invite @claude_assistant_test")
    print("2. Enable Socket Mode in your Slack app settings")
    print("3. Generate an app-level token with connections:write scope")
    print("4. Update the SLACK_APP_TOKEN in your .env file")

if __name__ == "__main__":
    test_bot()