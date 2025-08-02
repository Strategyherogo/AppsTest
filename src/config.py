import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Slack
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_app_token: str = os.getenv("SLACK_APP_TOKEN", "")
    slack_signing_secret: str = os.getenv("SLACK_SIGNING_SECRET", "")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Task Management
    todoist_api_key: str = os.getenv("TODOIST_API_KEY", "")
    notion_api_key: str = os.getenv("NOTION_API_KEY", "")
    trello_api_key: str = os.getenv("TRELLO_API_KEY", "")
    trello_api_token: str = os.getenv("TRELLO_API_TOKEN", "")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # App
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    use_simple_analyzer: bool = os.getenv("USE_SIMPLE_ANALYZER", "False").lower() == "true"

config = Config()