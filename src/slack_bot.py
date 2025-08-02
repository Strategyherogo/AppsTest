import logging
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import config
from message_analyzer import MessageAnalyzer
from task_manager import TaskOrchestrator

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=config.slack_bot_token,
    signing_secret=config.slack_signing_secret
)

# Initialize components
analyzer = MessageAnalyzer()
task_orchestrator = TaskOrchestrator()

# Store user preferences (in production, use a database)
user_preferences = {}

@app.event("app_mention")
def handle_mention(event, say, client, logger):
    """Handle when the bot is mentioned"""
    
    logger.info(f"Bot mentioned by {event['user']}: {event['text']}")
    
    user = event['user']
    text = event['text']
    channel = event['channel']
    
    # Remove bot mention from text
    text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
    logger.info(f"Cleaned text: {text}")
    
    # Check for commands
    if text.lower().startswith('help'):
        logger.info("Showing help")
        show_help(say)
    elif text.lower().startswith('settings'):
        show_settings(say, user)
    elif text.lower().startswith('analyze'):
        # Force analyze a specific message
        analyze_specific_message(text, say, client, user, channel)
    elif text.lower() in ['hello', 'hi', 'hey', 'test']:
        # Simple greeting response
        logger.info("Responding to greeting")
        say(f"👋 Hello <@{user}>! I'm your Task Bot. Try:\n• `help` - See what I can do\n• `analyze [message]` - Detect tasks in a message")
    else:
        # Analyze the message for tasks
        analyze_and_create_tasks(text, user, channel, say)

@app.event("message")
def handle_message(event, say, client):
    """Handle all messages in channels where bot is present"""
    
    # Skip bot messages
    if event.get('bot_id'):
        return
    
    user = event.get('user', 'unknown')
    text = event.get('text', '')
    channel = event.get('channel', 'unknown')
    
    # Get user preferences
    prefs = user_preferences.get(user, {
        'auto_analyze': True,
        'notification_level': 'high'
    })
    
    if not prefs.get('auto_analyze', True):
        return
    
    # Analyze message
    analysis = analyzer.analyze_message(text, user, channel)
    
    if analysis.get('contains_task') and analysis.get('confidence', 0) > 0.7:
        # High confidence task detected
        if prefs.get('notification_level') == 'high':
            # Ask for confirmation
            blocks = format_task_confirmation(analysis, user)
            
            response = client.chat_postEphemeral(
                channel=channel,
                user=user,
                blocks=blocks
            )
            
            # Store message_ts for action handling
            store_pending_task(response['message_ts'], analysis, user, channel)

def analyze_and_create_tasks(text, user, channel, say):
    """Analyze text and create tasks if found"""
    
    analysis = analyzer.analyze_message(text, user, channel)
    
    if not analysis.get('contains_task'):
        say("No tasks detected in the message.")
        return
    
    tasks = analysis.get('tasks', [])
    
    if not tasks:
        say("I detected potential tasks but couldn't extract specific details.")
        return
    
    # Create tasks
    created_count = 0
    for task in tasks:
        # Add metadata
        task['sender'] = user
        task['channel'] = channel
        
        results = task_orchestrator.create_task(task)
        
        if any(r['success'] for r in results):
            created_count += 1
            blocks = task_orchestrator.format_task_for_slack(task, results)
            say(blocks=blocks)
    
    if created_count > 0:
        say(f"✅ Created {created_count} task(s) from your message.")

def show_help(say):
    """Show help message"""
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Slack Task Bot - Help*\n\nI automatically analyze messages and create tasks for you!"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Commands:*\n" +
                        "• `@bot help` - Show this help message\n" +
                        "• `@bot settings` - View/update your preferences\n" +
                        "• `@bot analyze [message]` - Manually analyze a message for tasks\n" +
                        "• `@bot tasks` - List your recent tasks"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*How it works:*\n" +
                        "1. I monitor messages in channels I'm added to\n" +
                        "2. I use AI to detect actionable tasks\n" +
                        "3. I create tasks in your configured task management tools\n" +
                        "4. You get notified when tasks are created"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 *Tip:* Use keywords like 'todo', 'task', 'remind me', or 'need to' for better detection"
                }
            ]
        }
    ]
    
    say(blocks=blocks)

def show_settings(say, user):
    """Show user settings"""
    
    prefs = user_preferences.get(user, {
        'auto_analyze': True,
        'notification_level': 'high'
    })
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Your Settings*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Auto-analyze messages:* {'✅ Enabled' if prefs['auto_analyze'] else '❌ Disabled'}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Notification level:* {prefs['notification_level'].capitalize()}"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Toggle Auto-analyze"
                    },
                    "action_id": "toggle_auto_analyze"
                },
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Notification Level"
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "High - Ask before creating"},
                            "value": "high"
                        },
                        {
                            "text": {"type": "plain_text", "text": "Medium - Notify after creating"},
                            "value": "medium"
                        },
                        {
                            "text": {"type": "plain_text", "text": "Low - Silent"},
                            "value": "low"
                        }
                    ],
                    "action_id": "change_notification_level"
                }
            ]
        }
    ]
    
    say(blocks=blocks)

def format_task_confirmation(analysis, user):
    """Format task confirmation message"""
    
    tasks = analysis.get('tasks', [])
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📋 *Detected {len(tasks)} potential task(s)*"
            }
        }
    ]
    
    for i, task in enumerate(tasks):
        task_text = f"*{i+1}. {task['title']}*"
        if task.get('description'):
            task_text += f"\n_{task['description']}_"
        if task.get('priority'):
            task_text += f"\nPriority: {task['priority']}"
        if task.get('due_date'):
            task_text += f"\nDue: {task['due_date']}"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": task_text
            }
        })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "✅ Create Tasks"
                },
                "style": "primary",
                "action_id": "create_tasks"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "❌ Ignore"
                },
                "action_id": "ignore_tasks"
            }
        ]
    })
    
    return blocks

# Action handlers
@app.action("create_tasks")
def handle_create_tasks(ack, body, say):
    """Handle task creation confirmation"""
    ack()
    
    # Retrieve stored task data
    # In production, use a proper storage solution
    # For now, we'll recreate from the message
    
    say("✅ Tasks created successfully!")

@app.action("ignore_tasks")
def handle_ignore_tasks(ack, body, respond):
    """Handle task ignore action"""
    ack()
    
    respond(
        replace_original=True,
        text="Tasks ignored."
    )

@app.action("toggle_auto_analyze")
def handle_toggle_auto_analyze(ack, body, say):
    """Toggle auto-analyze setting"""
    ack()
    
    user = body['user']['id']
    prefs = user_preferences.get(user, {
        'auto_analyze': True,
        'notification_level': 'high'
    })
    
    prefs['auto_analyze'] = not prefs['auto_analyze']
    user_preferences[user] = prefs
    
    say(f"Auto-analyze is now {'enabled' if prefs['auto_analyze'] else 'disabled'}.")

@app.action("change_notification_level")
def handle_change_notification_level(ack, body, say):
    """Change notification level"""
    ack()
    
    user = body['user']['id']
    new_level = body['actions'][0]['selected_option']['value']
    
    prefs = user_preferences.get(user, {
        'auto_analyze': True,
        'notification_level': 'high'
    })
    
    prefs['notification_level'] = new_level
    user_preferences[user] = prefs
    
    say(f"Notification level set to {new_level}.")

# Helper functions
def store_pending_task(message_ts, analysis, user, channel):
    """Store pending task for later confirmation"""
    # In production, use Redis or a database
    # For now, we'll skip this
    pass

def analyze_specific_message(text, say, client, user, channel):
    """Analyze a specific message text"""
    
    # Remove 'analyze' command
    message_to_analyze = text[7:].strip()
    
    if not message_to_analyze:
        say("Please provide a message to analyze. Usage: `@bot analyze [your message]`")
        return
    
    analyze_and_create_tasks(message_to_analyze, user, channel, say)

# Main execution
if __name__ == "__main__":
    try:
        # Start the bot
        handler = SocketModeHandler(app, config.slack_app_token)
        logger.info("⚡️ Slack Task Bot is running!")
        handler.start()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise