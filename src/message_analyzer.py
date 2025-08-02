import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config import config

class MessageAnalyzer:
    def __init__(self):
        # Try to use OpenAI if configured, otherwise use local Llama
        self.use_openai = config.openai_api_key and config.openai_api_key != "your-openai-api-key"
        
        if self.use_openai:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.openai_api_key)
            print("✅ Using OpenAI for task detection")
        else:
            # Check if we should use simple analyzer
            if config.use_simple_analyzer:
                from simple_analyzer import SimpleMessageAnalyzer
                self.simple_analyzer = SimpleMessageAnalyzer()
                self.use_llama = False
                print("✅ Using simple keyword-based task detection")
            else:
                # Try Llama first, fall back to simple analyzer if it fails
                try:
                    from llama_analyzer import LlamaMessageAnalyzer
                    self.llama_analyzer = LlamaMessageAnalyzer()
                    self.use_llama = True
                    print("✅ Using local Llama model for task detection")
                except Exception as e:
                    print(f"⚠️ Llama initialization failed: {e}")
                    from simple_analyzer import SimpleMessageAnalyzer
                    self.simple_analyzer = SimpleMessageAnalyzer()
                    self.use_llama = False
                    print("✅ Falling back to simple keyword-based task detection")
        
        # Keywords that might indicate a task
        self.task_keywords = [
            "todo", "task", "remind", "remember", "need to", "should", "must",
            "have to", "don't forget", "please", "could you", "can you",
            "will you", "deadline", "by", "due", "asap", "urgent", "important"
        ]
        
        # Patterns for extracting dates
        self.date_patterns = [
            r'by (\d{1,2}/\d{1,2}/\d{2,4})',
            r'on (\d{1,2}/\d{1,2}/\d{2,4})',
            r'before (\d{1,2}/\d{1,2}/\d{2,4})',
            r'(tomorrow|today|next week|next month)',
            r'in (\d+) (days?|weeks?|months?)',
        ]
    
    def analyze_message(self, message: str, sender: str, channel: str) -> Dict:
        """Analyze a Slack message and extract potential tasks"""
        
        # Quick check if message might contain a task
        if not self._might_contain_task(message):
            return {"contains_task": False}
        
        # Use AI to analyze the message
        analysis = self._ai_analyze(message, sender, channel)
        
        # Extract any dates mentioned
        due_date = self._extract_date(message)
        if due_date:
            analysis["due_date"] = due_date
        
        return analysis
    
    def _might_contain_task(self, message: str) -> bool:
        """Quick check if message might contain a task"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.task_keywords)
    
    def _ai_analyze(self, message: str, sender: str, channel: str) -> Dict:
        """Use AI to analyze the message for tasks"""
        
        if self.use_openai:
            # Use OpenAI
            prompt = f"""Analyze this Slack message and determine if it contains any actionable tasks.
            
Message: "{message}"
Sender: {sender}
Channel: {channel}

Return a JSON object with:
1. contains_task: boolean - whether the message contains a task
2. tasks: array of task objects, each with:
   - title: string - short task title (max 50 chars)
   - description: string - detailed description
   - priority: string - "low", "medium", "high", or "urgent"
   - assignee: string - who should do the task (from context)
   - estimated_time: string - estimated time to complete (e.g., "30 minutes", "2 hours")
3. confidence: float - confidence score (0-1)
4. context: string - any relevant context extracted

Only extract explicit tasks, not general statements or questions."""

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a task extraction assistant. Extract only clear, actionable tasks from messages."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content)
                return result
                
            except Exception as e:
                print(f"OpenAI analysis error: {e}")
                return {
                    "contains_task": False,
                    "error": str(e)
                }
        else:
            # Use Llama or simple analyzer
            try:
                if hasattr(self, 'use_llama') and self.use_llama:
                    result = self.llama_analyzer.analyze_message(message, user_id=sender, channel_id=channel)
                else:
                    result = self.simple_analyzer.analyze_message(message, user_id=sender, channel_id=channel)
                
                # Convert simple analyzer format to expected format
                if result.get("is_task") and result.get("task_details"):
                    task_details = result["task_details"]
                    return {
                        "contains_task": True,
                        "tasks": [{
                            "title": task_details.get("title", "Untitled Task"),
                            "description": task_details.get("description", message),
                            "priority": task_details.get("priority", "medium"),
                            "assignee": sender,
                            "estimated_time": "Not specified"
                        }],
                        "confidence": result.get("confidence", 0.5),
                        "context": f"Detected in {channel}"
                    }
                else:
                    return {
                        "contains_task": False,
                        "confidence": result.get("confidence", 0.5)
                    }
                    
            except Exception as e:
                print(f"Simple analyzer error: {e}")
                return {
                    "contains_task": False,
                    "error": str(e)
                }
    
    def _extract_date(self, message: str) -> Optional[str]:
        """Extract date from message"""
        message_lower = message.lower()
        
        # Check for relative dates
        today = datetime.now()
        if "tomorrow" in message_lower:
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "today" in message_lower:
            return today.strftime("%Y-%m-%d")
        elif "next week" in message_lower:
            return (today + timedelta(weeks=1)).strftime("%Y-%m-%d")
        elif "next month" in message_lower:
            return (today + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Check for "in X days/weeks" pattern
        in_pattern = re.search(r'in (\d+) (days?|weeks?|months?)', message_lower)
        if in_pattern:
            amount = int(in_pattern.group(1))
            unit = in_pattern.group(2).rstrip('s')
            
            if unit == "day":
                return (today + timedelta(days=amount)).strftime("%Y-%m-%d")
            elif unit == "week":
                return (today + timedelta(weeks=amount)).strftime("%Y-%m-%d")
            elif unit == "month":
                return (today + timedelta(days=amount*30)).strftime("%Y-%m-%d")
        
        # Check for specific date patterns
        for pattern in self.date_patterns[:3]:  # Only the date-specific patterns
            match = re.search(pattern, message)
            if match:
                try:
                    # Parse and standardize the date
                    date_str = match.group(1)
                    # Add more sophisticated date parsing here if needed
                    return date_str
                except:
                    continue
        
        return None