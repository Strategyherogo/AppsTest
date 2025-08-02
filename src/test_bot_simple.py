#!/usr/bin/env python3
"""
Simple test of the Slack Task Bot AI functionality
No interactive input needed - just runs test messages
"""

import json
from datetime import datetime
from typing import Dict, List

# Mock the OpenAI client for testing
class MockOpenAI:
    class Completions:
        def create(self, **kwargs):
            # Simulate AI response based on the message
            message = kwargs.get('messages', [{}])[-1].get('content', '')
            
            test_responses = {
                "meeting": {
                    "is_task": True,
                    "confidence": 0.9,
                    "task_details": {
                        "title": "Schedule team meeting",
                        "description": "Need to schedule a team meeting to discuss the new project",
                        "priority": "medium",
                        "due_date": "2024-08-05",
                        "tags": ["meeting", "team"]
                    }
                },
                "reminder": {
                    "is_task": True,
                    "confidence": 0.85,
                    "task_details": {
                        "title": "Send report to client",
                        "description": "Remember to send the monthly report to the client",
                        "priority": "high",
                        "due_date": "2024-08-02",
                        "tags": ["report", "client"]
                    }
                },
                "normal": {
                    "is_task": False,
                    "confidence": 0.95,
                    "task_details": None
                }
            }
            
            # Determine response based on keywords
            response_key = "normal"
            if "meeting" in message.lower():
                response_key = "meeting"
            elif "remember" in message.lower() or "reminder" in message.lower():
                response_key = "reminder"
            
            response = test_responses[response_key]
            
            class MockChoice:
                class Message:
                    content = json.dumps(response)
                message = Message()
            
            class MockResponse:
                choices = [MockChoice()]
            
            return MockResponse()
    
    def __init__(self, api_key=None):
        self.chat = self
        self.completions = self.Completions()

# Simple message analyzer for testing
class TestMessageAnalyzer:
    def __init__(self):
        self.client = MockOpenAI()
    
    def analyze_message(self, message: str, user_id: str = "test_user") -> Dict:
        """Analyze a message using the mock AI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a task detection AI."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Error analyzing message: {e}")
            return {
                "is_task": False,
                "confidence": 0.0,
                "task_details": None
            }

# Test messages
test_messages = [
    "Hey, can we schedule a team meeting for next week to discuss the new project?",
    "Remember to send the monthly report to the client by Friday",
    "Just finished the presentation, looks good!",
    "Don't forget to review the pull request when you get a chance",
    "The weather is nice today",
    "Can you help me with the budget planning tomorrow at 2pm?"
]

def run_tests():
    print("🤖 Slack Task Bot - Local Test Mode")
    print("="*50)
    print("Testing AI task detection on sample messages...")
    print("="*50)
    
    analyzer = TestMessageAnalyzer()
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📨 Test Message {i}:")
        print(f"   '{message}'")
        
        # Analyze the message
        result = analyzer.analyze_message(message)
        
        print(f"\n   🔍 Analysis Result:")
        print(f"      Is Task: {result['is_task']}")
        print(f"      Confidence: {result['confidence']:.1%}")
        
        if result['is_task'] and result['task_details']:
            details = result['task_details']
            print(f"\n   📝 Task Details:")
            print(f"      Title: {details['title']}")
            print(f"      Priority: {details['priority']}")
            print(f"      Due Date: {details.get('due_date', 'Not specified')}")
            print(f"      Tags: {', '.join(details.get('tags', []))}")
        
        print("-"*50)
    
    print("\n✅ Test completed!")
    print("\nThis demonstrates how the bot would analyze Slack messages.")
    print("In production, it would use real OpenAI API for more accurate detection.")

if __name__ == "__main__":
    run_tests()