import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import os

class LlamaMessageAnalyzer:
    """
    Local Llama-based message analyzer for task detection
    Uses llama.cpp for efficient CPU inference
    """
    
    def __init__(self):
        """Initialize the Llama model"""
        print("🤖 Initializing local Llama model...")
        
        # Download a small, efficient model for task detection
        # Using Phi-3 mini (3.8B params) - good balance of quality and speed
        model_name = "microsoft/Phi-3-mini-4k-instruct-gguf"
        model_file = "Phi-3-mini-4k-instruct-q4.gguf"
        
        # Check if model exists locally
        model_path = f"models/{model_file}"
        if not os.path.exists(model_path):
            print(f"📥 Downloading {model_name}...")
            os.makedirs("models", exist_ok=True)
            
            # Download from HuggingFace
            downloaded_path = hf_hub_download(
                repo_id=model_name,
                filename=model_file,
                local_dir="models"
            )
            print(f"✅ Model downloaded to {downloaded_path}")
        
        # Initialize Llama with the model
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window
            n_threads=4,  # CPU threads
            n_gpu_layers=0,  # CPU only
            verbose=False
        )
        print("✅ Llama model loaded successfully!")
    
    def analyze_message(self, message: str, user_id: str = None, 
                       channel_id: str = None, thread_ts: str = None) -> Dict:
        """
        Analyze a message to determine if it contains a task
        
        Args:
            message: The message text to analyze
            user_id: ID of the user who sent the message
            channel_id: ID of the channel where the message was sent
            thread_ts: Thread timestamp if the message is in a thread
            
        Returns:
            Dictionary containing analysis results
        """
        
        # Create a focused prompt for task detection
        prompt = f"""<|system|>
You are a task detection assistant. Analyze the following message and determine if it contains a task or action item.
Return a JSON object with these fields:
- is_task: boolean (true if the message contains a task)
- confidence: float between 0 and 1
- task_details: object with title, description, priority (low/medium/high), due_date (YYYY-MM-DD or null), and tags array

Be strict - only mark clear action items as tasks. General information or discussions are not tasks.
<|end|>
<|user|>
Message: "{message}"
<|end|>
<|assistant|>"""

        try:
            # Generate response
            response = self.llm(
                prompt,
                max_tokens=300,
                temperature=0.1,  # Low temperature for consistent output
                stop=["<|end|>", "<|user|>", "<|system|>"]
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            # Try to parse as JSON
            try:
                # Find JSON in the response
                json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    # Fallback parsing
                    result = self._parse_natural_response(generated_text, message)
            except json.JSONDecodeError:
                # Fallback to natural language parsing
                result = self._parse_natural_response(generated_text, message)
            
            # Ensure all required fields
            return self._validate_result(result)
            
        except Exception as e:
            print(f"❌ Error analyzing message: {e}")
            # Return safe default
            return {
                "is_task": False,
                "confidence": 0.0,
                "task_details": None,
                "analysis_metadata": {
                    "model": "llama-local",
                    "error": str(e)
                }
            }
    
    def _parse_natural_response(self, text: str, original_message: str) -> Dict:
        """Parse natural language response when JSON parsing fails"""
        
        # Simple keyword detection as fallback
        task_keywords = ['todo', 'task', 'remind', 'deadline', 'due', 'please', 
                        'need', 'should', 'must', 'will', 'can you', 'could you']
        
        text_lower = text.lower()
        message_lower = original_message.lower()
        
        # Check if model thinks it's a task
        is_task = any(phrase in text_lower for phrase in ['is a task', 'contains a task', 'action item'])
        
        # If not clear from response, check original message
        if not is_task:
            is_task = any(keyword in message_lower for keyword in task_keywords)
        
        # Extract priority
        priority = "medium"
        if any(word in message_lower for word in ['urgent', 'asap', 'critical', 'important']):
            priority = "high"
        elif any(word in message_lower for word in ['whenever', 'eventually', 'low priority']):
            priority = "low"
        
        # Extract due date
        due_date = None
        date_patterns = [
            (r'tomorrow', 1),
            (r'next week', 7),
            (r'next month', 30),
            (r'by friday', None),  # Would need more complex logic
            (r'end of day', 0)
        ]
        
        for pattern, days in date_patterns:
            if re.search(pattern, message_lower) and days is not None:
                due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
                break
        
        if is_task:
            # Create a simple title from the message
            title = original_message[:50].strip()
            if len(original_message) > 50:
                title += "..."
            
            return {
                "is_task": True,
                "confidence": 0.7,
                "task_details": {
                    "title": title,
                    "description": original_message,
                    "priority": priority,
                    "due_date": due_date,
                    "tags": self._extract_tags(original_message)
                }
            }
        
        return {
            "is_task": False,
            "confidence": 0.8,
            "task_details": None
        }
    
    def _extract_tags(self, message: str) -> List[str]:
        """Extract relevant tags from the message"""
        tags = []
        
        # Common categories
        tag_patterns = {
            'meeting': ['meeting', 'call', 'sync', 'standup'],
            'email': ['email', 'send', 'reply'],
            'review': ['review', 'check', 'approve'],
            'development': ['code', 'implement', 'fix', 'bug'],
            'documentation': ['document', 'write', 'update docs']
        }
        
        message_lower = message.lower()
        for tag, keywords in tag_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                tags.append(tag)
        
        return tags[:5]  # Limit to 5 tags
    
    def _validate_result(self, result: Dict) -> Dict:
        """Ensure the result has all required fields"""
        
        # Default structure
        validated = {
            "is_task": result.get("is_task", False),
            "confidence": float(result.get("confidence", 0.0)),
            "task_details": None,
            "analysis_metadata": {
                "model": "llama-local",
                "model_name": "Phi-3-mini-4k",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Validate confidence is between 0 and 1
        validated["confidence"] = max(0.0, min(1.0, validated["confidence"]))
        
        # Add task details if it's a task
        if validated["is_task"] and result.get("task_details"):
            details = result["task_details"]
            validated["task_details"] = {
                "title": str(details.get("title", "Untitled Task")),
                "description": str(details.get("description", "")),
                "priority": details.get("priority", "medium"),
                "due_date": details.get("due_date"),
                "tags": details.get("tags", [])
            }
            
            # Validate priority
            if validated["task_details"]["priority"] not in ["low", "medium", "high"]:
                validated["task_details"]["priority"] = "medium"
        
        return validated

    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences for task detection"""
        # For now, return defaults - could be extended to store in database
        return {
            "auto_detect_tasks": True,
            "confidence_threshold": 0.7,
            "notification_level": "medium",
            "preferred_task_manager": "todoist"
        }