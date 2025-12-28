#!/usr/bin/env python3
"""
Test LM Studio service directly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/anirudhchhabra/Projects/simplitrip/simplitrip/backend')

try:
    from services.lmstudio_service import lmstudio_service, chat, is_available, health
    print("✅ Successfully imported lmstudio_service")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Testing LM Studio Service")
print("=" * 60)

# Test 1: Check if LM Studio is available
print("\n[TEST 1] Checking if LM Studio is available...")
try:
    available = is_available()
    print(f"  LM Studio available: {available}")
    if not available:
        print("  ⚠️  LM Studio is not responding!")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 2: Health check
print("\n[TEST 2] Health check...")
try:
    health_status = health()
    print(f"  Health status: {health_status}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 3: Chat function
print("\n[TEST 3] Testing chat function...")
try:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, say hello back to me"}
    ]
    print(f"  Sending {len(messages)} messages...")
    response = chat(messages=messages, max_tokens=256, temperature=0.7)
    print(f"  Response type: {type(response)}")
    print(f"  Response: {response}")
    
    if isinstance(response, dict):
        text = response.get('text')
        print(f"  Text field: '{text}'")
        if text:
            print(f"  ✅ Got response: {text[:100]}")
        else:
            print(f"  ❌ Text field is empty!")
    else:
        print(f"  ❌ Response is not a dict: {type(response)}")
        
except Exception as e:
    import traceback
    print(f"  ❌ Error: {e}")
    print(f"  Traceback:\n{traceback.format_exc()}")

print("\n" + "=" * 60)
