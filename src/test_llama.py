#!/usr/bin/env python3
"""
Test Llama model for task detection
"""

import sys
import os

print("🤖 Testing Llama Task Detection")
print("="*50)

# Test messages
test_messages = [
    "Hey team, we need to finish the quarterly report by next Friday. Can someone take the lead on this?",
    "Just had a great meeting with the client!",
    "Don't forget to submit your timesheet by end of day",
    "The weather is nice today",
    "Can you review my pull request when you get a chance? It's blocking the release.",
    "Let's schedule a team lunch next week to celebrate the launch"
]

try:
    print("📥 Initializing Llama model...")
    print("This may take a moment on first run as it downloads the model...")
    
    from llama_analyzer import LlamaMessageAnalyzer
    analyzer = LlamaMessageAnalyzer()
    
    print("\n📝 Analyzing messages:")
    print("-"*50)
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{i}. Message: '{msg}'")
        
        # Analyze the message
        result = analyzer.analyze_message(msg)
        
        print(f"   Is Task: {result['is_task']} (confidence: {result['confidence']:.1%})")
        
        if result['is_task'] and result['task_details']:
            details = result['task_details']
            print(f"   📌 Task Details:")
            print(f"      Title: {details['title']}")
            print(f"      Priority: {details['priority']}")
            print(f"      Due Date: {details.get('due_date', 'Not specified')}")
            print(f"      Tags: {', '.join(details.get('tags', []))}")
    
    print("\n✅ Llama model test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFalling back to simple analyzer would happen in production.")
    
    # Show what simple analyzer would do
    print("\n🔄 Testing with simple analyzer instead...")
    from simple_analyzer import SimpleMessageAnalyzer
    simple = SimpleMessageAnalyzer()
    
    for msg in test_messages[:3]:  # Just test first 3
        result = simple.analyze_message(msg)
        print(f"\nMessage: '{msg[:50]}...'")
        print(f"Is Task: {result['is_task']} (confidence: {result['confidence']:.1%})")