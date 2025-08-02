from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests
import json
from datetime import datetime
from config import config

class TaskManager(ABC):
    """Abstract base class for task management integrations"""
    
    @abstractmethod
    def create_task(self, task: Dict) -> Dict:
        pass
    
    @abstractmethod
    def list_tasks(self) -> List[Dict]:
        pass

class TodoistManager(TaskManager):
    """Todoist integration for task management"""
    
    def __init__(self):
        self.api_key = config.todoist_api_key
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_task(self, task: Dict) -> Dict:
        """Create a task in Todoist"""
        
        priority_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "urgent": 4
        }
        
        todoist_task = {
            "content": task.get("title", ""),
            "description": task.get("description", ""),
            "priority": priority_map.get(task.get("priority", "medium"), 2),
            "due_string": task.get("due_date", "today")
        }
        
        response = requests.post(
            f"{self.base_url}/tasks",
            headers=self.headers,
            json=todoist_task
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to create Todoist task: {response.text}")
    
    def list_tasks(self) -> List[Dict]:
        """List all active tasks"""
        response = requests.get(
            f"{self.base_url}/tasks",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to list Todoist tasks: {response.text}")

class NotionManager(TaskManager):
    """Notion integration for task management"""
    
    def __init__(self, database_id: str = None):
        self.api_key = config.notion_api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def create_task(self, task: Dict) -> Dict:
        """Create a task in Notion database"""
        
        notion_page = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": task.get("title", "")
                            }
                        }
                    ]
                },
                "Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": task.get("description", "")
                            }
                        }
                    ]
                },
                "Priority": {
                    "select": {
                        "name": task.get("priority", "medium").capitalize()
                    }
                },
                "Due Date": {
                    "date": {
                        "start": task.get("due_date", datetime.now().strftime("%Y-%m-%d"))
                    }
                },
                "Status": {
                    "select": {
                        "name": "To Do"
                    }
                },
                "Source": {
                    "select": {
                        "name": "Slack"
                    }
                },
                "Created From": {
                    "rich_text": [
                        {
                            "text": {
                                "content": f"Channel: {task.get('channel', 'Unknown')}, Sender: {task.get('sender', 'Unknown')}"
                            }
                        }
                    ]
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/pages",
            headers=self.headers,
            json=notion_page
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to create Notion task: {response.text}")
    
    def list_tasks(self) -> List[Dict]:
        """List tasks from Notion database"""
        
        query = {
            "filter": {
                "property": "Status",
                "select": {
                    "does_not_equal": "Done"
                }
            },
            "sorts": [
                {
                    "property": "Due Date",
                    "direction": "ascending"
                }
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/databases/{self.database_id}/query",
            headers=self.headers,
            json=query
        )
        
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            raise Exception(f"Failed to list Notion tasks: {response.text}")

class TaskOrchestrator:
    """Orchestrates task creation across multiple platforms"""
    
    def __init__(self):
        self.managers = []
        
        # Initialize available task managers
        if config.todoist_api_key:
            self.managers.append(TodoistManager())
        
        if config.notion_api_key:
            # You'll need to set the database_id
            # self.managers.append(NotionManager(database_id="your-database-id"))
            pass
    
    def create_task(self, task_data: Dict) -> List[Dict]:
        """Create task across all configured platforms"""
        results = []
        
        for manager in self.managers:
            try:
                result = manager.create_task(task_data)
                results.append({
                    "platform": manager.__class__.__name__,
                    "success": True,
                    "data": result
                })
            except Exception as e:
                results.append({
                    "platform": manager.__class__.__name__,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def format_task_for_slack(self, task: Dict, results: List[Dict]) -> str:
        """Format task creation results for Slack message"""
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Task Created:* {task.get('title', 'Untitled')}"
                }
            }
        ]
        
        if task.get('description'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": task['description']
                }
            })
        
        # Add task details
        fields = []
        if task.get('priority'):
            fields.append({
                "type": "mrkdwn",
                "text": f"*Priority:* {task['priority']}"
            })
        if task.get('due_date'):
            fields.append({
                "type": "mrkdwn",
                "text": f"*Due Date:* {task['due_date']}"
            })
        
        if fields:
            blocks.append({
                "type": "section",
                "fields": fields
            })
        
        # Add creation results
        success_platforms = [r['platform'] for r in results if r['success']]
        failed_platforms = [r['platform'] for r in results if not r['success']]
        
        if success_platforms:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"✅ Created in: {', '.join(success_platforms)}"
                    }
                ]
            })
        
        if failed_platforms:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"❌ Failed in: {', '.join(failed_platforms)}"
                    }
                ]
            })
        
        return blocks