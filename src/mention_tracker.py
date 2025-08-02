import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import config
from simple_analyzer import SimpleMessageAnalyzer
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=config.slack_bot_token,
    signing_secret=config.slack_signing_secret
)

# Initialize components
analyzer = SimpleMessageAnalyzer()

# Store user mentions (in production, use a database)
user_mentions = defaultdict(list)
tracked_users = set()  # Users who have enabled mention tracking

# Auto-track Evgeny
tracked_users.add('U04NYQN6NEM')  # Evgeny Goncharov - auto-enabled

@app.event("app_mention")
def handle_bot_mention(event, say, client, logger):
    """Handle when the bot is mentioned"""
    
    user = event['user']
    text = event['text']
    channel = event['channel']
    
    # Remove bot mention from text
    text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
    logger.info(f"Bot mentioned by {user}: {text}")
    
    # Commands
    if text.lower() in ['track me', 'track my mentions', 'start tracking']:
        enable_mention_tracking(user, say, client)
    elif text.lower() in ['stop tracking', 'untrack me']:
        disable_mention_tracking(user, say)
    elif text.lower() in ['my mentions', 'show mentions', 'list mentions']:
        show_user_mentions(user, say, client)
    elif text.lower() in ['my tasks', 'show tasks', 'task list']:
        show_task_list(user, say, client)
    elif text.lower().startswith('clear'):
        clear_mentions(user, say)
    elif text.lower() in ['help', 'commands']:
        show_help(say)
    else:
        say(f"👋 Hi <@{user}>! Type `help` to see what I can do.")

def enable_mention_tracking(user_id: str, say, client):
    """Enable mention tracking for a user"""
    tracked_users.add(user_id)
    
    # Get user info
    try:
        user_info = client.users_info(user=user_id)
        user_name = user_info['user']['real_name']
    except:
        user_name = user_id
    
    say(f"✅ <@{user_id}>, I'm now tracking your mentions across all channels I can see.\n"
        f"I'll analyze them and help you create tasks from important mentions.\n\n"
        f"Commands:\n"
        f"• `my mentions` - See all your recent mentions\n"
        f"• `my tasks` - See mentions that look like tasks\n"
        f"• `clear mentions` - Clear your mention history")

def disable_mention_tracking(user_id: str, say):
    """Disable mention tracking for a user"""
    tracked_users.discard(user_id)
    user_mentions[user_id].clear()
    say(f"❌ <@{user_id}>, I've stopped tracking your mentions and cleared your history.")

@app.event("message")
def handle_message(event, client, logger):
    """Monitor all messages for user mentions"""
    
    # Skip bot messages
    if event.get('bot_id'):
        return
    
    text = event.get('text', '')
    channel = event.get('channel')
    sender = event.get('user')
    ts = event.get('ts')
    
    # Find all user mentions in the message
    mentions = re.findall(r'<@([A-Z0-9]+)>', text)
    
    for mentioned_user in mentions:
        # Only track if user has opted in
        if mentioned_user in tracked_users:
            logger.info(f"Found mention of tracked user {mentioned_user}")
            
            # Get channel name
            try:
                channel_info = client.conversations_info(channel=channel)
                channel_name = channel_info['channel']['name']
            except:
                channel_name = channel
            
            # Get sender name
            try:
                sender_info = client.users_info(user=sender)
                sender_name = sender_info['user']['real_name']
            except:
                sender_name = sender
            
            # Clean the message text
            clean_text = text.replace(f'<@{mentioned_user}>', '@you')
            
            # Analyze if it's a task
            analysis = analyzer.analyze_message(clean_text)
            
            # Store the mention
            mention_data = {
                'timestamp': ts,
                'channel': channel,
                'channel_name': channel_name,
                'sender': sender,
                'sender_name': sender_name,
                'text': text,
                'clean_text': clean_text,
                'is_task': analysis['is_task'],
                'confidence': analysis['confidence'],
                'task_details': analysis.get('task_details'),
                'permalink': None
            }
            
            # Try to get permalink
            try:
                permalink_resp = client.chat_getPermalink(
                    channel=channel,
                    message_ts=ts
                )
                mention_data['permalink'] = permalink_resp['permalink']
            except:
                pass
            
            user_mentions[mentioned_user].append(mention_data)
            
            # Keep only last 100 mentions per user
            if len(user_mentions[mentioned_user]) > 100:
                user_mentions[mentioned_user] = user_mentions[mentioned_user][-100:]

def show_user_mentions(user_id: str, say, client):
    """Show all recent mentions of a user"""
    
    if user_id not in tracked_users:
        say(f"<@{user_id}>, I'm not tracking your mentions yet. Say `track me` to start!")
        return
    
    mentions = user_mentions.get(user_id, [])
    
    if not mentions:
        say(f"<@{user_id}>, you haven't been mentioned recently.")
        return
    
    # Get last 10 mentions
    recent_mentions = mentions[-10:]
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Your recent mentions* (last {len(recent_mentions)} of {len(mentions)} total):"
            }
        },
        {"type": "divider"}
    ]
    
    for mention in reversed(recent_mentions):
        timestamp = datetime.fromtimestamp(float(mention['timestamp']))
        time_str = timestamp.strftime('%b %d at %I:%M %p')
        
        # Create mention block
        mention_text = f"*In #{mention['channel_name']}* - {time_str}\n"
        mention_text += f"From: {mention['sender_name']}\n"
        mention_text += f"_{mention['clean_text']}_"
        
        if mention['is_task']:
            mention_text += " 📝 *[Possible Task]*"
        
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": mention_text
            }
        }
        
        if mention['permalink']:
            block["accessory"] = {
                "type": "button",
                "text": {"type": "plain_text", "text": "View"},
                "url": mention['permalink']
            }
        
        blocks.append(block)
        blocks.append({"type": "divider"})
    
    say(blocks=blocks)

def show_task_list(user_id: str, say, client):
    """Show mentions that look like tasks"""
    
    if user_id not in tracked_users:
        say(f"<@{user_id}>, I'm not tracking your mentions yet. Say `track me` to start!")
        return
    
    mentions = user_mentions.get(user_id, [])
    task_mentions = [m for m in mentions if m['is_task']]
    
    if not task_mentions:
        say(f"<@{user_id}>, no task-like mentions found. I look for keywords like 'please', 'need to', 'by Friday', etc.")
        return
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📝 Your Task Mentions* ({len(task_mentions)} tasks found):"
            }
        },
        {"type": "divider"}
    ]
    
    # Group by priority
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for mention in task_mentions:
        task_details = mention.get('task_details', {})
        priority = task_details.get('priority', 'medium')
        
        task_item = {
            'mention': mention,
            'details': task_details
        }
        
        if priority == 'high':
            high_priority.append(task_item)
        elif priority == 'low':
            low_priority.append(task_item)
        else:
            medium_priority.append(task_item)
    
    # Add high priority tasks
    if high_priority:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*🔴 High Priority:*"}
        })
        for item in high_priority:
            blocks.append(create_task_block(item['mention'], item['details']))
    
    # Add medium priority tasks
    if medium_priority:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*🟡 Medium Priority:*"}
        })
        for item in medium_priority:
            blocks.append(create_task_block(item['mention'], item['details']))
    
    # Add low priority tasks
    if low_priority:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*🟢 Low Priority:*"}
        })
        for item in low_priority:
            blocks.append(create_task_block(item['mention'], item['details']))
    
    # Add export option
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "_Tasks are automatically detected based on keywords and context._"
        }
    })
    
    say(blocks=blocks)

def create_task_block(mention: Dict, task_details: Dict) -> Dict:
    """Create a Slack block for a task"""
    
    timestamp = datetime.fromtimestamp(float(mention['timestamp']))
    time_str = timestamp.strftime('%b %d')
    
    task_text = f"• {task_details.get('title', mention['clean_text'][:50])}\n"
    task_text += f"  _From {mention['sender_name']} in #{mention['channel_name']} on {time_str}_"
    
    if task_details.get('due_date'):
        task_text += f"\n  📅 Due: {task_details['due_date']}"
    
    block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": task_text
        }
    }
    
    if mention['permalink']:
        block["accessory"] = {
            "type": "button",
            "text": {"type": "plain_text", "text": "View", "emoji": True},
            "url": mention['permalink']
        }
    
    return block

def clear_mentions(user_id: str, say):
    """Clear all mentions for a user"""
    user_mentions[user_id].clear()
    say(f"✅ <@{user_id}>, I've cleared all your tracked mentions.")

def show_help(say):
    """Show help message"""
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🤖 Mention Tracker Bot*\n\nI can track when you're mentioned across all channels and help you identify tasks."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Commands:*\n"
                        "• `track me` - Start tracking your mentions\n"
                        "• `my mentions` - See your recent mentions\n"
                        "• `my tasks` - See mentions that look like tasks\n"
                        "• `clear mentions` - Clear your mention history\n"
                        "• `stop tracking` - Stop tracking and clear data\n"
                        "• `help` - Show this message"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*How it works:*\n"
                        "1. When you enable tracking, I monitor all channels I'm in\n"
                        "2. I save messages where you're mentioned\n"
                        "3. I analyze them to identify potential tasks\n"
                        "4. You can review and act on them anytime"
            }
        }
    ]
    
    say(blocks=blocks)

if __name__ == "__main__":
    handler = SocketModeHandler(app, config.slack_app_token)
    logger.info("⚡️ Mention Tracker Bot is running!")
    print("\n✅ Bot is running! Commands:")
    print("- @bot track me - Start tracking your mentions")
    print("- @bot my mentions - See recent mentions")
    print("- @bot my tasks - See task-like mentions")
    handler.start()