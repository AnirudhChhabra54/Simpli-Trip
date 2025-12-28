#!/usr/bin/env python3
"""
Test script to verify the chat flow end-to-end
"""
import json
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

def test_chat_flow():
    print("=" * 60)
    print("Testing Chat Flow: Frontend → Backend → LM Studio")
    print("=" * 60)
    
    session_id = f"test-{int(time.time())}"
    
    # Test 1: Send first message
    print("\n[TEST 1] Sending initial message...")
    payload = {
        "session_id": session_id,
        "message": "I want to visit Goa for 3 days"
    }
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{API_BASE}/chat/continue", json=payload, timeout=30)
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            reply = data.get("reply")
            if reply:
                print(f"  ✅ Got reply: {reply[:100]}...")
            else:
                print(f"  ❌ Reply is empty or missing!")
                print(f"  Full response: {data}")
        else:
            print(f"  ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test 2: Send follow-up message
    print("\n[TEST 2] Sending follow-up message...")
    payload = {
        "session_id": session_id,
        "message": "My budget is 20000 rupees"
    }
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{API_BASE}/chat/continue", json=payload, timeout=30)
        print(f"  Status: {response.status_code}")
        
        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            reply = data.get("reply")
            if reply:
                print(f"  ✅ Got reply: {reply[:100]}...")
            else:
                print(f"  ❌ Reply is empty or missing!")
        else:
            print(f"  ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Chat flow test completed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_chat_flow()
