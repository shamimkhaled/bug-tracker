#!/usr/bin/env python3
"""
Quick test to verify middleware is working
"""

import asyncio
import websockets
import json
import requests
import re

async def test_middleware():
    print("🧪 Testing WebSocket Middleware...")
    
    # Test 1: Anonymous connection (should fail)
    print("\n1️⃣ Testing anonymous connection...")
    try:
        async with websockets.connect('ws://localhost:8000/ws/project/1/') as ws:
            print("❌ Anonymous connection should have failed!")
    except Exception as e:
        print(f"✅ Anonymous connection properly rejected: {e}")
    
    # Test 2: With session key (should work)
    print("\n2️⃣ Testing with session key...")
    
    # Get session key first
    session = requests.Session()
    
    # Login
    response = session.get('http://localhost:8000/admin/login/')
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
    
    if csrf_match:
        csrf_token = csrf_match.group(1)
        login_data = {
            'username': 'shamimkhaled',  # Update with your username
            'password': '9999',          # Update with your password
            'csrfmiddlewaretoken': csrf_token,
            'next': '/admin/'
        }
        
        login_response = session.post('http://localhost:8000/admin/login/', data=login_data)
        
        if 'login' not in login_response.url:
            session_key = session.cookies.get('sessionid')
            print(f"🔑 Got session key: {session_key}")
            
            # Test with session key in query
            ws_url = f'ws://localhost:8000/ws/project/1/?session_key={session_key}'
            
            try:
                async with websockets.connect(ws_url) as ws:
                    print("✅ Connection with session key successful!")
                    
                    # Wait for welcome message
                    message = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(message)
                    print(f"📨 Received: {data}")
                    
                    if data.get('type') == 'connection_established':
                        print("🎉 Middleware is working correctly!")
                        return True
                    
            except Exception as e:
                print(f"❌ Connection with session key failed: {e}")
        else:
            print("❌ Login failed")
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_middleware())
    if success:
        print("\n✅ Middleware test PASSED!")
    else:
        print("\n❌ Middleware test FAILED!")
        print("\nTroubleshooting:")
        print("1. Make sure Django server is running")
        print("2. Check username/password in script")
        print("3. Look at Django logs for middleware messages")