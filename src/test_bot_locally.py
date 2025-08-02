#!/usr/bin/env python3
"""
Local test version of the Slack Task Bot
Tests the AI message analysis without needing Slack credentials
"""

import json
import os
from datetime import datetime
from typing import Dict, List

# Mock the config for testing
class MockConfig:
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    debug = True
    log_level = "INFO"

# Import our modules with mocked config
import sys
sys.modules['config'] = sys.modules[__name__]
config = MockConfig()

from message_analyzer import MessageAnalyzer

def print_header():
    """Print welcome header"""
    print("\n" + "="*60)
    print("🤖 Slack Task Bot - Local Test Mode")
    print("="*60)
    print("This is a test version that simulates the bot locally.")
    print("Type messages to analyze them for tasks.")
    print("Commands: 'help', 'examples', 'quit'\n")

def print_task_result(analysis: Dict):
    """Pretty print the task analysis result"""
    
    if not analysis.get('contains_task'):
        print("❌ No tasks detected in this message.\n")
        return
    
    tasks = analysis.get('tasks', [])
    confidence = analysis.get('confidence', 0)
    
    print(f"\n✅ Found {len(tasks)} task(s) (Confidence: {confidence:.0%})")
    print("-" * 40)
    
    for i, task in enumerate(tasks, 1):
        print(f"\n📋 Task {i}:")
        print(f"   Title: {task.get('title', 'N/A')}")
        
        if task.get('description'):
            print(f"   Description: {task['description']}")
        
        if task.get('priority'):
            priority_emoji = {
                'low': '🟢',
                'medium': '🟡', 
                'high': '🟠',
                'urgent': '🔴'
            }.get(task['priority'], '⚪')
            print(f"   Priority: {priority_emoji} {task['priority'].capitalize()}")
        
        if task.get('assignee'):
            print(f"   Assignee: {task['assignee']}")
        
        if task.get('estimated_time'):
            print(f"   Estimated Time: {task['estimated_time']}")
        
        if task.get('due_date'):
            print(f"   Due Date: {task['due_date']}")
    
    if analysis.get('context'):
        print(f"\n💭 Context: {analysis['context']}")
    
    print("\n" + "-" * 40 + "\n")

def show_examples():
    """Show example messages"""
    examples = [
        "Can you remind me to review the Q4 budget by Friday? It's urgent.",
        "TODO: Update documentation for the new API endpoints",
        "We need to schedule a meeting with the design team next week",
        "Please send me the report by tomorrow morning",
        "Don't forget to submit your timesheet by 5 PM today",
        "Task: Implement user authentication with OAuth2",
        "I should probably refactor the payment processing module soon",
        "URGENT: Fix the production bug in the checkout flow ASAP"
    ]
    
    print("\n📝 Example messages to try:")
    print("-" * 40)
    for example in examples:
        print(f"• {example}")
    print()

def show_help():
    """Show help information"""
    print("\n📖 Help:")
    print("-" * 40)
    print("This test bot analyzes messages for actionable tasks.")
    print("\nThe AI looks for:")
    print("• Action words: todo, task, remind, need to, should, must")
    print("• Urgency indicators: urgent, asap, important, deadline")
    print("• Time references: tomorrow, next week, by Friday")
    print("• Task patterns: clear action items with subjects and verbs")
    print("\nCommands:")
    print("• 'help' - Show this help")
    print("• 'examples' - Show example messages")
    print("• 'quit' - Exit the test bot\n")

def test_without_openai():
    """Test with mock responses when OpenAI is not configured"""
    
    print("\n⚠️  OpenAI API key not configured!")
    print("Using mock responses for demonstration.\n")
    
    mock_responses = {
        "remind": {
            "contains_task": True,
            "tasks": [{
                "title": "Review Q4 budget",
                "description": "Review and analyze the Q4 budget documents",
                "priority": "high",
                "assignee": "You",
                "estimated_time": "2 hours",
                "due_date": "2024-01-26"
            }],
            "confidence": 0.9,
            "context": "Budget review requested with Friday deadline"
        },
        "todo": {
            "contains_task": True,
            "tasks": [{
                "title": "Update API documentation",
                "description": "Update documentation for the new API endpoints",
                "priority": "medium",
                "assignee": "You",
                "estimated_time": "1 hour"
            }],
            "confidence": 0.95,
            "context": "Documentation task identified"
        },
        "meeting": {
            "contains_task": True,
            "tasks": [{
                "title": "Schedule design team meeting",
                "description": "Schedule a meeting with the design team for next week",
                "priority": "medium",
                "assignee": "You",
                "estimated_time": "30 minutes",
                "due_date": "next week"
            }],
            "confidence": 0.85,
            "context": "Meeting scheduling request"
        },
        "default": {
            "contains_task": False,
            "confidence": 0.2,
            "context": "No clear actionable tasks detected"
        }
    }
    
    while True:
        try:
            message = input("📨 Enter message (or command): ").strip()
            
            if not message:
                continue
            
            if message.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif message.lower() == 'help':
                show_help()
                continue
            elif message.lower() == 'examples':
                show_examples()
                continue
            
            # Simple mock logic
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['remind', 'remember', 'don\'t forget']):
                result = mock_responses['remind'].copy()
            elif any(word in message_lower for word in ['todo', 'task', 'implement']):
                result = mock_responses['todo'].copy()
            elif any(word in message_lower for word in ['meeting', 'schedule', 'call']):
                result = mock_responses['meeting'].copy()
            else:
                result = mock_responses['default'].copy()
            
            # Customize based on message
            if result['contains_task'] and result['tasks']:
                # Extract a better title from the message
                words = message.split()
                if len(words) > 3:
                    result['tasks'][0]['title'] = ' '.join(words[:5]) + '...'
            
            print_task_result(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

def main():
    """Main function to run the local test bot"""
    
    print_header()
    
    # Check if OpenAI is configured
    if not config.openai_api_key:
        print("💡 Tip: Set OPENAI_API_KEY environment variable for real AI analysis")
        print("   export OPENAI_API_KEY='your-api-key'\n")
        test_without_openai()
        return
    
    # Initialize the analyzer
    try:
        analyzer = MessageAnalyzer()
        print("✅ AI Message Analyzer initialized successfully!\n")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        print("Running in mock mode instead...\n")
        test_without_openai()
        return
    
    # Main interaction loop
    while True:
        try:
            message = input("📨 Enter message (or command): ").strip()
            
            if not message:
                continue
                
            if message.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif message.lower() == 'help':
                show_help()
                continue
            elif message.lower() == 'examples':
                show_examples()
                continue
            
            # Analyze the message
            print("\n🔍 Analyzing message...")
            
            analysis = analyzer.analyze_message(
                message=message,
                sender="test_user",
                channel="test_channel"
            )
            
            print_task_result(analysis)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error analyzing message: {e}\n")

if __name__ == "__main__":
    main()