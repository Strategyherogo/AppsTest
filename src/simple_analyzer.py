import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class SimpleMessageAnalyzer:
    """
    Simple rule-based message analyzer for task detection
    No AI required - uses keywords and patterns
    """
    
    def __init__(self):
        # Task keywords
        self.task_keywords = [
            "todo", "task", "remind", "remember", "need to", "should", "must",
            "have to", "don't forget", "please", "could you", "can you",
            "will you", "deadline", "by", "due", "asap", "urgent", "important",
            "schedule", "meeting", "call", "email", "send", "review", "check",
            "prepare", "finish", "complete", "fix", "update", "create"
        ]
        
        # Priority indicators
        self.high_priority_words = ["urgent", "asap", "critical", "important", "immediately"]
        self.low_priority_words = ["whenever", "eventually", "if possible", "when you can"]
        
        print("✅ Using simple keyword-based task detection (no AI)")
    
    def analyze_message(self, message: str, user_id: str = None, 
                       channel_id: str = None, thread_ts: str = None) -> Dict:
        """
        Analyze a message using keyword detection
        """
        message_lower = message.lower()
        
        # Check if message contains task keywords
        task_score = sum(1 for keyword in self.task_keywords if keyword in message_lower)
        is_task = task_score >= 2  # At least 2 keywords
        
        # Single strong indicators
        strong_indicators = ["remind me", "don't forget", "need to", "have to", "please"]
        if any(indicator in message_lower for indicator in strong_indicators):
            is_task = True
        
        # Questions are usually not tasks
        if message.strip().endswith("?") and not any(kw in message_lower for kw in ["could you", "can you", "will you"]):
            is_task = False
        
        # Determine confidence
        confidence = min(0.9, 0.3 + (task_score * 0.15))
        
        if is_task:
            # Extract task details
            task_details = self._extract_task_details(message)
            
            return {
                "is_task": True,
                "confidence": confidence,
                "task_details": task_details,
                "analysis_metadata": {
                    "model": "simple-rules",
                    "keyword_matches": task_score,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "is_task": False,
                "confidence": 1.0 - confidence,
                "task_details": None,
                "analysis_metadata": {
                    "model": "simple-rules",
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def _extract_task_details(self, message: str) -> Dict:
        """Extract task details from the message"""
        message_lower = message.lower()
        
        # Create title (first 50 chars or first sentence)
        title = message.split('.')[0][:50]
        if len(title) == 50:
            title = title.rsplit(' ', 1)[0] + "..."
        
        # Determine priority
        priority = "medium"
        if any(word in message_lower for word in self.high_priority_words):
            priority = "high"
        elif any(word in message_lower for word in self.low_priority_words):
            priority = "low"
        
        # Extract due date
        due_date = self._extract_due_date(message)
        
        # Extract tags
        tags = self._extract_tags(message)
        
        return {
            "title": title.strip(),
            "description": message,
            "priority": priority,
            "due_date": due_date,
            "tags": tags
        }
    
    def _extract_due_date(self, message: str) -> Optional[str]:
        """Extract due date from message"""
        message_lower = message.lower()
        today = datetime.now()
        
        # Time-based patterns
        patterns = [
            (r'\btoday\b', 0),
            (r'\btomorrow\b', 1),
            (r'\bnext week\b', 7),
            (r'\bnext month\b', 30),
            (r'\bmonday\b', None),
            (r'\btuesday\b', None),
            (r'\bwednesday\b', None),
            (r'\bthursday\b', None),
            (r'\bfriday\b', None),
            (r'\bend of day\b', 0),
            (r'\beod\b', 0),
            (r'\bend of week\b', None),
            (r'\beow\b', None),
        ]
        
        for pattern, days in patterns:
            if re.search(pattern, message_lower):
                if days is not None:
                    due_date = today + timedelta(days=days)
                    return due_date.strftime('%Y-%m-%d')
                else:
                    # Handle day names - find next occurrence
                    if 'monday' in pattern:
                        days_ahead = (0 - today.weekday()) % 7
                    elif 'tuesday' in pattern:
                        days_ahead = (1 - today.weekday()) % 7
                    elif 'wednesday' in pattern:
                        days_ahead = (2 - today.weekday()) % 7
                    elif 'thursday' in pattern:
                        days_ahead = (3 - today.weekday()) % 7
                    elif 'friday' in pattern:
                        days_ahead = (4 - today.weekday()) % 7
                    elif 'end of week' in pattern or 'eow' in pattern:
                        days_ahead = (4 - today.weekday()) % 7
                    else:
                        continue
                    
                    if days_ahead == 0:
                        days_ahead = 7  # Next week
                    
                    due_date = today + timedelta(days=days_ahead)
                    return due_date.strftime('%Y-%m-%d')
        
        # "in X days/hours" pattern
        in_pattern = re.search(r'in (\d+) (hours?|days?|weeks?)', message_lower)
        if in_pattern:
            amount = int(in_pattern.group(1))
            unit = in_pattern.group(2).rstrip('s')
            
            if unit == 'hour':
                due_date = today + timedelta(hours=amount)
            elif unit == 'day':
                due_date = today + timedelta(days=amount)
            elif unit == 'week':
                due_date = today + timedelta(weeks=amount)
            
            return due_date.strftime('%Y-%m-%d')
        
        # Specific date patterns (MM/DD, MM-DD)
        date_pattern = re.search(r'(\d{1,2})[/-](\d{1,2})', message)
        if date_pattern:
            month = int(date_pattern.group(1))
            day = int(date_pattern.group(2))
            year = today.year
            
            # If date is in the past, assume next year
            try:
                due_date = datetime(year, month, day)
                if due_date < today:
                    due_date = datetime(year + 1, month, day)
                return due_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        return None
    
    def _extract_tags(self, message: str) -> List[str]:
        """Extract relevant tags from the message"""
        tags = []
        message_lower = message.lower()
        
        # Tag patterns
        tag_patterns = {
            'meeting': ['meeting', 'call', 'sync', 'standup', 'discussion'],
            'email': ['email', 'mail', 'send', 'reply', 'respond'],
            'review': ['review', 'check', 'approve', 'feedback'],
            'development': ['code', 'implement', 'fix', 'bug', 'feature', 'deploy'],
            'documentation': ['document', 'docs', 'write', 'update docs'],
            'planning': ['plan', 'schedule', 'organize', 'prepare'],
            'research': ['research', 'investigate', 'analyze', 'find out']
        }
        
        for tag, keywords in tag_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                tags.append(tag)
        
        # Add priority as tag if high/urgent
        if any(word in message_lower for word in ['urgent', 'asap', 'critical']):
            tags.append('urgent')
        
        return list(set(tags))[:5]  # Unique tags, max 5
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences for task detection"""
        return {
            "auto_detect_tasks": True,
            "confidence_threshold": 0.6,
            "notification_level": "medium",
            "preferred_task_manager": "todoist"
        }