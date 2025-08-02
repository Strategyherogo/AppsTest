# Slack Task Bot

An intelligent Slack bot that automatically analyzes messages and creates tasks in your preferred task management system.

## Features

- 🤖 **AI-Powered Analysis**: Uses GPT-4 to intelligently detect tasks in messages
- 📝 **Multiple Task Managers**: Supports Todoist, Notion, Trello (extensible)
- ⚡ **Real-time Processing**: Monitors messages as they come in
- 🎯 **Smart Detection**: Recognizes keywords, deadlines, and priorities
- 🔧 **Customizable**: Per-user settings for notification preferences
- 📊 **Confidence Scoring**: Only creates tasks when confidence is high

## Setup

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "Task Bot") and select your workspace

### 2. Configure OAuth & Permissions

Add these Bot Token Scopes:
- `app_mentions:read` - Read messages that mention your bot
- `channels:history` - View messages in public channels
- `chat:write` - Send messages
- `groups:history` - View messages in private channels
- `im:history` - View direct messages
- `mpim:history` - View group direct messages

### 3. Enable Socket Mode

1. Go to "Socket Mode" in your app settings
2. Enable Socket Mode
3. Generate an app-level token with `connections:write` scope
4. Save the token (starts with `xapp-`)

### 4. Enable Event Subscriptions

Subscribe to these bot events:
- `app_mention` - When someone mentions your bot
- `message.channels` - Messages in public channels
- `message.groups` - Messages in private channels
- `message.im` - Direct messages
- `message.mpim` - Group direct messages

### 5. Install App to Workspace

1. Go to "Install App" in your app settings
2. Click "Install to Workspace"
3. Authorize the app
4. Save the Bot User OAuth Token (starts with `xoxb-`)

### 6. Set Up Environment

```bash
# Clone the repository
cd slack-task-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your tokens
```

### 7. Configure Task Management

Choose and configure at least one:

#### Todoist
1. Get API key from [todoist.com/prefs/integrations](https://todoist.com/prefs/integrations)
2. Add to `.env`: `TODOIST_API_KEY=your-key`

#### Notion
1. Create integration at [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a database with properties: Title, Description, Priority, Due Date, Status, Source
3. Share database with your integration
4. Add to `.env`: `NOTION_API_KEY=your-key`

#### OpenAI
1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Add to `.env`: `OPENAI_API_KEY=your-key`

## Usage

### Starting the Bot

```bash
python src/slack_bot.py
```

### Commands

- `@bot help` - Show help message
- `@bot settings` - View/update preferences
- `@bot analyze [message]` - Manually analyze a message
- `@bot tasks` - List recent tasks

### How It Works

1. **Message Detection**: Bot monitors channels it's added to
2. **AI Analysis**: GPT-4 analyzes messages for actionable tasks
3. **Task Extraction**: Extracts title, description, priority, and due dates
4. **Confirmation**: High-confidence tasks prompt for confirmation
5. **Creation**: Tasks are created in your configured systems

### Task Detection Keywords

The bot looks for phrases like:
- "todo", "task", "remind me"
- "need to", "should", "must", "have to"
- "don't forget", "please", "could you"
- "deadline", "by", "due", "asap", "urgent"

### Example Messages

```
"@bot Can you remind me to review the Q4 budget by Friday? It's urgent."
→ Creates task: "Review Q4 budget" with high priority, due Friday

"TODO: Update documentation for the new API endpoints"
→ Creates task: "Update documentation for the new API endpoints"

"We need to schedule a meeting with the design team next week"
→ Creates task: "Schedule meeting with design team" due next week
```

## Deployment Options

### 1. Local Development
Perfect for testing and small teams

### 2. Cloud Deployment

#### Heroku
```bash
# Create app
heroku create your-slack-task-bot

# Set environment variables
heroku config:set SLACK_BOT_TOKEN=xoxb-...
heroku config:set SLACK_APP_TOKEN=xapp-...
# ... set other variables

# Deploy
git push heroku main
```

#### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["python", "src/slack_bot.py"]
```

#### AWS Lambda
Use [Serverless Framework](https://serverless.com/) for easy deployment

## Security Notes

- Never commit `.env` files
- Use environment variables in production
- Rotate tokens regularly
- Limit bot permissions to minimum required
- Use encrypted storage for user preferences

## Extending the Bot

### Adding New Task Managers

1. Inherit from `TaskManager` base class
2. Implement `create_task()` and `list_tasks()`
3. Add initialization in `TaskOrchestrator`

### Improving Task Detection

1. Modify `task_keywords` in `MessageAnalyzer`
2. Update the AI prompt for better extraction
3. Add new date pattern recognition

## Troubleshooting

- **Bot not responding**: Check Socket Mode connection
- **No tasks detected**: Verify OpenAI API key
- **Task creation fails**: Check task manager API keys
- **Missing messages**: Verify bot has correct permissions

## License

MIT