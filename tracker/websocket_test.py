import asyncio
import websockets
import json
import requests
import re
from datetime import datetime

class WebSocketTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.session = requests.Session()
        self.session_key = None
        
        
    def login_and_get_session(self, username="shamimkhaled", password="9999"):
        """Login and extract session key for WebSocket authentication"""
        print(f"Logging in as {username}...")
        
        try:
            # Get login page
            login_url = f"{self.base_url}/admin/login/"
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                print(f"Cannot access admin: {response.status_code}")
                return False
            
            # Extract CSRF token
            csrf_pattern = r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']'
            csrf_match = re.search(csrf_pattern, response.text)
            
            if not csrf_match:
                print("CSRF token not found")
                return False
            
            csrf_token = csrf_match.group(1)
            
            # Login
            login_data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': csrf_token,
                'next': '/admin/'
            }
            
            login_response = self.session.post(login_url, data=login_data)
            
            # Check login success
            if 'login' not in login_response.url:
                print("Login successful!")
                
                # Extract session key
                cookies = self.session.cookies.get_dict()
                self.session_key = cookies.get('sessionid')
                
                if self.session_key:
                    print(f"Session key: {self.session_key}")
                    print(f"All cookies: {list(cookies.keys())}")
                    return True
                else:
                    print("No session key found in cookies")
                    return False
            else:
                print("Login failed")
                return False
                
        except Exception as e:
            print(f"Login error: {e}")
            return False
        
        
        
    
    async def test_websocket_with_session(self, project_id=1):
        """Test WebSocket connection with session authentication"""
        print(f"\nTesting WebSocket with session authentication...")
        
        if not self.session_key:
            print(" No session key available")
            return False
        
        # First try with query string method (more reliable)
        print("\n Trying with session key in query string...")
        success = await self.test_websocket_with_query_auth(project_id)
        
        if success:
            return True
        
        
        
        # If query method fails, try headers method with proper websockets version handling
        print("\n Trying with cookie headers...")
        return await self.test_websocket_with_headers(project_id)
    
    
    
    
    
    async def test_websocket_with_query_auth(self, project_id=1):
        """Test WebSocket with session key in query string"""
        ws_url = f"{self.ws_url}/ws/project/{project_id}/?session_key={self.session_key}"
        print(f"🔗 Connecting with query auth: {ws_url}")
        
        try:
            # Use websockets.connect without extra_headers to avoid version issues
            async with websockets.connect(ws_url) as ws:
                print(" WebSocket connected with query auth!")
                
                try:
                    welcome_msg = await asyncio.wait_for(ws.recv(), timeout=10)
                    welcome_data = json.loads(welcome_msg)
                    print(f" Welcome: {json.dumps(welcome_data, indent=2)}")
                    
                    if welcome_data.get('type') == 'connection_established':
                        print(" Query authentication successful!")
                        await self.run_websocket_tests(ws)
                        return True
                    else:
                        print(f" Unexpected message: {welcome_data}")
                        return False
                        
                except asyncio.TimeoutError:
                    print(" No welcome message received")
                    return False
                    
        except Exception as e:
            print(f" Query auth failed: {e}")
            return False
        
        
        
    
    async def test_websocket_with_headers(self, project_id=1):
        """Test WebSocket with cookie headers (for newer websockets versions)"""
        cookies = self.session.cookies.get_dict()
        cookie_header = '; '.join([f"{k}={v}" for k, v in cookies.items()])
        
        ws_url = f"{self.ws_url}/ws/project/{project_id}/"
        print(f" Connecting with headers to: {ws_url}")
        print(f" Using cookies: {cookie_header[:100]}...")
        
        try:
            # Check websockets version and use appropriate method
            import websockets
            websockets_version = websockets.__version__
            print(f"📦 Websockets version: {websockets_version}")
            
            # Try with headers if supported
            try:
                headers = {
                    'Cookie': cookie_header,
                    'Origin': 'http://localhost:8000'
                }
                
                # This will work with newer websockets versions
                async with websockets.connect(ws_url, extra_headers=headers) as ws:
                    print("WebSocket connected with headers!")
                    return await self.handle_websocket_connection(ws)
                    
            except TypeError as e:
                if 'extra_headers' in str(e):
                    print(" Your websockets version doesn't support extra_headers")
                    print(" Please upgrade: pip install --upgrade websockets")
                    return False
                else:
                    raise e
                    
        except Exception as e:
            print(f"Header auth failed: {e}")
            return False
        
        
        
        
    
    async def handle_websocket_connection(self, ws):
        """Handle the WebSocket connection after it's established"""
        try:
            welcome_msg = await asyncio.wait_for(ws.recv(), timeout=10)
            welcome_data = json.loads(welcome_msg)
            print(f" Welcome: {json.dumps(welcome_data, indent=2)}")
            
            if welcome_data.get('type') == 'connection_established':
                print("Authentication successful!")
                await self.run_websocket_tests(ws)
                return True
            else:
                print(f"Unexpected message: {welcome_data}")
                return False
                
        except asyncio.TimeoutError:
            print("No welcome message received")
            return False
        
        
        
        
    
    async def run_websocket_tests(self, ws):
        """Run various WebSocket tests"""
        print("\n Running WebSocket tests...")
        
        # Test 1: Ping-Pong
        print("\nTesting Ping-Pong...")
        ping_msg = {
            'type': 'ping',
            'timestamp': datetime.now().isoformat()
        }
        
        await ws.send(json.dumps(ping_msg))
        print(f"Sent: {ping_msg}")
        
        try:
            pong_msg = await asyncio.wait_for(ws.recv(), timeout=5)
            pong_data = json.loads(pong_msg)
            print(f"Received: {json.dumps(pong_data, indent=2)}")
            
            if pong_data.get('type') == 'pong':
                print("Ping-Pong successful!")
            else:
                print("Unexpected pong response")
        except asyncio.TimeoutError:
            print("Ping-Pong timeout")
        
        # Test 2: Typing Indicators
        print("\nTesting Typing Indicators...")
        typing_msg = {
            'type': 'typing_indicator',
            'is_typing': True,
            'bug_id': 1
        }
        
        await ws.send(json.dumps(typing_msg))
        print(f"Sent typing start: {typing_msg}")
        
        await asyncio.sleep(2)
        
        typing_msg['is_typing'] = False
        await ws.send(json.dumps(typing_msg))
        print(f"Sent typing stop: {typing_msg}")
        
        print("Typing indicators sent successfully!")
        
        
        
        
        
    
    def test_api_endpoints(self):
        """Test API endpoints to verify they can trigger WebSocket notifications"""
        print(f"\nTesting API endpoints...")
        
        # Get JWT token
        try:
            token_response = self.session.post(f"{self.base_url}/api/auth/login/", json={
                'username': 'shamimkhaled',
                'password': '9999'
            })
            
            if token_response.status_code == 200:
                jwt_token = token_response.json()['access']
                headers = {'Authorization': f'Bearer {jwt_token}'}
                print(f"Got JWT token")
                
                # Test creating a bug
                bug_data = {
                    'title': 'WebSocket Test Bug',
                    'description': 'Testing real-time notifications',
                    'priority': 'High',
                    'project': 1
                }
                
                bug_response = self.session.post(
                    f"{self.base_url}/api/bugs/",
                    json=bug_data,
                    headers=headers
                )
                
                if bug_response.status_code == 201:
                    bug_info = bug_response.json()
                    print(f"Bug created: #{bug_info['id']} - {bug_info['title']}")
                    print("This should trigger a WebSocket notification!")
                    return True
                else:
                    print(f" Failed to create bug: {bug_response.status_code}")
                    print(f"Response: {bug_response.text}")
                    return False
            else:
                print(f" Failed to get JWT token: {token_response.status_code}")
                return False
                
        except Exception as e:
            print(f" API test error: {e}")
            return False







async def main():
    """Main test runner"""
    print("WEBSOCKET TEST WITH SESSION DEBUGGING")
    print("=" * 60)
    
    # Check websockets version
    try:
        import websockets
        print(f" Websockets version: {websockets.__version__}")
    except Exception as e:
        print(f" Websockets import error: {e}")
        return
    
    tester = WebSocketTest()
    
    # Step 1: Login and get session
    print("\nSTEP 1: Authentication & Session")
    print("-" * 40)
    if not tester.login_and_get_session():
        print("\n Authentication failed")
        print("\nSetup instructions:")
        print("1. Make sure your Django server is running")
        print("2. Make sure you have admin access for user 'shamimkhaled'")
        print("3. Create test project if needed")
        return
    
    # Step 2: Test WebSocket
    print("\nSTEP 2: WebSocket Connection")
    print("-" * 40)
    ws_success = await tester.test_websocket_with_session(1)
    
    
    if ws_success:
        print("\n WebSocket tests successful!")
        
        # Step 3: Test API integration
        print("\nSTEP 3: API Integration")
        print("-" * 40)
        api_success = tester.test_api_endpoints()
        
        
        if api_success:
            print("\n ALL TESTS PASSED!")
            print("Your WebSocket system is working perfectly!")
            
        else:
            print("\n API tests failed")
            
            
    else:
        print("\n WebSocket tests failed")
        print("\nDebugging tips:")
        print("1. Check Redis: redis-cli ping")
        print("2. Check Django logs for detailed errors")
        print("3. Make sure the middleware is properly configured")
        print("4. Upgrade websockets: pip install --upgrade websockets")




if __name__ == "__main__":
    asyncio.run(main())