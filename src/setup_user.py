#!/usr/bin/env python3
"""
Get user ID for setup
"""

import os
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()

client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

print("Finding your user ID...")

# Search for Evgeny
try:
    users = client.users_list()
    
    for user in users['members']:
        if not user.get('is_bot') and not user.get('deleted'):
            real_name = user.get('real_name', '').lower()
            display_name = user.get('profile', {}).get('display_name', '').lower()
            
            if 'evgeny' in real_name or 'evgeny' in display_name:
                print(f"\nFound: {user['real_name']}")
                print(f"User ID: {user['id']}")
                print(f"Username: @{user['name']}")
                print(f"\nAdd this to mention_tracker.py:")
                print(f"tracked_users.add('{user['id']}')  # {user['real_name']}")
                
except Exception as e:
    print(f"Error: {e}")