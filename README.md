# 🐛 Bug Tracker - Complete Setup & Testing Guide

A comprehensive Django REST API with real-time WebSocket support for bug tracking.

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Database Setup](#database-setup)
5. [API Documentation](#api-documentation)
6. [WebSocket Testing](#websocket-testing)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

### Features
- ✅ **REST API**: Complete CRUD operations for Projects, Bugs, and Comments
- ✅ **Real-time Updates**: WebSocket notifications for bug changes and comments
- ✅ **JWT Authentication**: Secure API access
- ✅ **Advanced Filtering**: Search and filter capabilities
- ✅ **Activity Logging**: Track all activities with real-time streaming
- ✅ **API Documentation**: Swagger/OpenAPI documentation
- ✅ **Typing Indicators**: Real-time typing indicators in comments

### Architecture
```
Frontend ↔ Django Channels (WebSocket) ↔ Redis ↔ Django REST API ↔ Database
```

---

## 🔧 Prerequisites

Before starting, ensure you have:

- **Python 3.8+** installed
- **Git** installed
- **Redis Server** (we'll install this)
- **Code Editor** (VS Code, PyCharm, etc.)
- **API Testing Tool** (Postman, Insomnia, or curl)

---

## 🚀 Installation & Setup

### Step 1: Clone and Setup Project

```bash
# Clone the repository
git clone <your-repository-url>
cd bugtracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install Redis Server

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### On macOS:
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Redis
brew install redis
brew services start redis
```

#### On Windows:
```bash
# Download Redis from: https://github.com/microsoftarchive/redis/releases
# Install and run redis-server.exe
```

#### Verify Redis Installation:
```bash
redis-cli ping
# Should return: PONG
```

### Step 3: Environment Setup

Create `.env` file in project root:
```env
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://127.0.0.1:6379/0
```

### Step 4: Django Configuration

Check your `requirements.txt` includes and install the dependencies:
```
 pip install -r requirements.txt
```

---

## 💾 Database Setup

### Step 1: Create Database Tables

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Step 2: Create Superuser

```bash
python manage.py createsuperuser
# Enter username, email, and password when prompted
```

### Step 3: Create Test Users

```bash
python manage.py shell
```

In the Python shell, run:
```python
from django.contrib.auth.models import User
from tracker.models import Project

# Create test users
user1 = User.objects.create_user('testuser1', 'test1@example.com', '9999')
user2 = User.objects.create_user('testuser2', 'test2@example.com', '9999')
user3 = User.objects.create_user('testuser3', 'test3@example.com', '9999')

# Create test project
project = Project.objects.create(
    name='Test Project',
    description='A project for testing WebSocket and API functionality',
    owner=user1
)

print("✅ Test users and project created successfully!")
print(f"📁 Project ID: {project.id}")
print(f"👤 Users: {[u.username for u in [user1, user2, user3]]}")

# Exit shell
exit()
```

### Step 4: Start Django Server

```bash
python manage.py runserver
```

You should see:
```
Starting ASGI/Daphne version 4.0.0 development server at http://127.0.0.1:8000/
```

**Important**: Look for "ASGI/Daphne" - this means WebSocket support is enabled!

### Step 5: Run Daphne directly and redis server

***Instead of using Django's development server, you can run Daphne directly for WebSocket testing and real-time monitoring notification in terminal during API testing:***
```
# Stop Django development server first (Ctrl+C)

# Run redis 
redis-server 

# Run Daphne directly
daphne -b 0.0.0.0 -p 8000 bugtracker.asgi:application

# With verbose logging
daphne -v 2 -b 0.0.0.0 -p 8000 bugtracker.asgi:application
```

**And test to websocket connection to run the websocket_test.py**
```
python tracker/websocket_test.py
```


## 🌐 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication

#### 1. Get JWT Token
**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
    "username": "testuser1",
    "password": "9999"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 2. Refresh Token
**Endpoint:** `POST /api/auth/refresh/`

**Request:**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Projects API

#### 1. List Projects
**Endpoint:** `GET /api/projects/`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Test Project",
        "description": "A project for testing",
        "owner": {
            "id": 1,
            "username": "testuser1",
            "email": "test1@example.com",
            "first_name": "",
            "last_name": ""
        },
        "bugs_count": 0,
        "created_at": "2024-08-03T10:30:00.123456Z",
        "updated_at": "2024-08-03T10:30:00.123456Z"
    }
]
```

#### 2. Create Project
**Endpoint:** `POST /api/projects/`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

**Request:**
```json
{
    "name": "My New Project",
    "description": "Description of my new project"
}
```

**Response (201 Created):**
```json
{
    "id": 2,
    "name": "My New Project",
    "description": "Description of my new project",
    "owner": {
        "id": 1,
        "username": "testuser1",
        "email": "test1@example.com",
        "first_name": "",
        "last_name": ""
    },
    "bugs_count": 0,
    "created_at": "2024-08-03T11:00:00.123456Z",
    "updated_at": "2024-08-03T11:00:00.123456Z"
}
```

### Bugs API

#### 1. List Bugs
**Endpoint:** `GET /api/bugs/`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

**Query Parameters:**
- `?status=Open` - Filter by status
- `?priority=High` - Filter by priority
- `?project=1` - Filter by project ID
- `?assigned_to=1` - Filter by assigned user
- `?search=keyword` - Search in title/description

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "Login button not working",
        "description": "When users click login, nothing happens",
        "status": "Open",
        "priority": "High",
        "assigned_to": {
            "id": 2,
            "username": "testuser2",
            "email": "test2@example.com",
            "first_name": "",
            "last_name": ""
        },
        "project": 1,
        "project_name": "Test Project",
        "created_by": {
            "id": 1,
            "username": "testuser1",
            "email": "test1@example.com",
            "first_name": "",
            "last_name": ""
        },
        "comments_count": 0,
        "created_at": "2024-08-03T12:00:00.123456Z",
        "updated_at": "2024-08-03T12:00:00.123456Z"
    }
]
```

#### 2. Create Bug (Triggers WebSocket Notification!)
**Endpoint:** `POST /api/bugs/`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

**Request:**
```json
{
    "title": "Database connection timeout",
    "description": "Users experiencing timeout when saving data",
    "priority": "Critical",
    "project": 1,
    "assigned_to_id": 2
}
```

**Response (201 Created):**
```json
{
    "id": 2,
    "title": "Database connection timeout",
    "description": "Users experiencing timeout when saving data",
    "status": "Open",
    "priority": "Critical",
    "assigned_to": {
        "id": 2,
        "username": "testuser2",
        "email": "test2@example.com",
        "first_name": "",
        "last_name": ""
    },
    "project": 1,
    "project_name": "Test Project",
    "created_by": {
        "id": 1,
        "username": "testuser1",
        "email": "test1@example.com",
        "first_name": "",
        "last_name": ""
    },
    "comments_count": 0,
    "created_at": "2024-08-03T12:30:00.123456Z",
    "updated_at": "2024-08-03T12:30:00.123456Z"
}
```

#### 3. Update Bug Status (Triggers WebSocket Notification!)
**Endpoint:** `PATCH /api/bugs/1/`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

**Request:**
```json
{
    "status": "In Progress"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Login button not working",
    "description": "When users click login, nothing happens",
    "status": "In Progress",
    "priority": "High",
    "assigned_to": {
        "id": 2,
        "username": "testuser2",
        "email": "test2@example.com",
        "first_name": "",
        "last_name": ""
    },
    "project": 1,
    "project_name": "Test Project",
    "created_by": {
        "id": 1,
        "username": "testuser1",
        "email": "test1@example.com",
        "first_name": "",
        "last_name": ""
    },
    "comments_count": 0,
    "created_at": "2024-08-03T12:00:00.123456Z",
    "updated_at": "2024-08-03T12:45:00.123456Z"
}
```

#### 4. Get Assigned Bugs
**Endpoint:** `GET /api/bugs/assigned_to_me/`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

### Comments API

#### 1. Add Comment (Triggers WebSocket Notification!)
**Endpoint:** `POST /api/comments/`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

**Request:**
```json
{
    "bug": 1,
    "message": "I'm investigating this issue. Found the root cause in authentication module."
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "bug": 1,
    "commenter": {
        "id": 1,
        "username": "testuser1",
        "email": "test1@example.com",
        "first_name": "",
        "last_name": ""
    },
    "message": "I'm investigating this issue. Found the root cause in authentication module.",
    "created_at": "2024-08-03T13:00:00.123456Z",
    "updated_at": "2024-08-03T13:00:00.123456Z"
}
```

#### 2. List Comments
**Endpoint:** `GET /api/comments/?bug=1`
**Headers:** `Authorization: Bearer YOUR_JWT_TOKEN`

---

## 🔌 WebSocket Testing

### Connection URL
```
ws://localhost:8000/ws/project/{project_id}/
```

### Authentication Methods

#### Method 1: Browser Console (After Admin Login)
1. **Login to Django Admin:**
   ```
   http://localhost:8000/admin/
   ```

2. **Open Browser Console (F12) and run:**
   ```javascript
   // Connect to WebSocket
   const ws = new WebSocket('ws://localhost:8000/ws/project/1/');

   // Event handlers
   ws.onopen = function(event) {
       console.log('✅ Connected to WebSocket');
   };

   ws.onmessage = function(event) {
       const data = JSON.parse(event.data);
       console.log('📨 Received:', data);
   };

   ws.onerror = function(error) {
       console.log('❌ Error:', error);
   };

   ws.onclose = function(event) {
       console.log('🔌 Disconnected:', event.code);
   };
   ```

#### Method 2: With Session Key
```javascript
// If you have session key
const sessionKey = 'your-session-key-here';
const ws = new WebSocket(`ws://localhost:8000/ws/project/1/?session_key=${sessionKey}`);
```

### WebSocket Message Examples

#### Send Ping
```javascript
ws.send(JSON.stringify({
    type: 'ping',
    timestamp: new Date().toISOString()
}));
```

#### Send Typing Indicator
```javascript
// Start typing
ws.send(JSON.stringify({
    type: 'typing_indicator',
    is_typing: true,
    bug_id: 1
}));

// Stop typing (after 3 seconds)
setTimeout(() => {
    ws.send(JSON.stringify({
        type: 'typing_indicator',
        is_typing: false,
        bug_id: 1
    }));
}, 3000);
```

### WebSocket Notifications You'll Receive

#### Bug Created Notification
```json
{
    "type": "bug_notification",
    "event_type": "bug_created",
    "bug": {
        "id": 2,
        "title": "New Bug Title",
        "status": "Open",
        "priority": "High"
    },
    "user": "testuser1",
    "timestamp": "2024-08-03T13:30:00.123456Z"
}
```

#### Comment Added Notification
```json
{
    "type": "comment_notification",
    "comment": {
        "id": 1,
        "message": "This is a new comment",
        "created_at": "2024-08-03T13:35:00.123456Z"
    },
    "bug": {
        "id": 1,
        "title": "Login button not working"
    },
    "user": "testuser2"
}
```

#### Typing Indicator
```json
{
    "type": "typing_indicator",
    "user": "testuser2",
    "is_typing": true,
    "bug_id": 1,
    "timestamp": "2024-08-03T13:40:00.123456Z"
}
```



### Testing Workflow

1. **Run Authentication → Login** (saves JWT token)
2. **Run Projects → Create Project** (saves project ID)
3. **Open WebSocket connection in browser** (as shown above)
4. **Run Bugs → Create Bug** (should trigger WebSocket notification)
5. **Run Comments → Add Comment** (should trigger WebSocket notification)
6. **Run Bugs → Update Bug Status** (should trigger WebSocket notification)

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Redis Connection Error
```
Error: ConnectionRefusedError: [Errno 61] Connection refused
```
**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start Redis:
# Ubuntu/Linux:
sudo systemctl start redis-server
# macOS:
brew services start redis
# Windows: Start redis-server.exe
```

#### 2. WebSocket Connection Failed
```
WebSocket connection to 'ws://localhost:8000/ws/project/1/' failed
```
**Solutions:**
1. **Check Django server startup message:**
   - Should show "ASGI/Daphne" not "WSGI"
   - If showing WSGI, check if `daphne` is in INSTALLED_APPS

2. **Authentication issue:**
   - Login to Django admin first: `/admin/`
   - Or use session key in WebSocket URL

3. **Check middleware configuration:**
   - Ensure WebSocket middleware is properly configured

#### 3. No WebSocket Notifications
**Solutions:**
1. **Check Redis:** `redis-cli ping`
2. **Check Django logs** for middleware messages
3. **Verify WebSocket connection** is established first
4. **Test API endpoints** to trigger notifications

#### 4. JWT Token Expired
```
HTTP 401 Unauthorized
```
**Solution:**
- Get new token: `POST /api/auth/login/`
- Or refresh existing token: `POST /api/auth/refresh/`

### Debug Steps

1. **Check all services are running:**
```bash
# Redis
redis-cli ping

# Django (should show ASGI)
python manage.py runserver
```

2. **Test API without WebSocket:**
```bash
curl -X GET http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **Test WebSocket connection:**
- Use browser console method
- Check browser network tab for WebSocket connection

4. **Check Django logs:**
- Look for middleware authentication messages
- Check for any error traces

---

## 🎉 Success Indicators

### ✅ Everything Working Correctly

**Django Server Startup:**
```
Starting ASGI/Daphne version 4.0.0 development server at http://127.0.0.1:8000/
```

**Redis Check:**
```bash
redis-cli ping
# Returns: PONG
```

**WebSocket Connection:**
```javascript
// Browser console shows:
✅ Connected to WebSocket
📨 Received: {
  "type": "connection_established",
  "message": "Connected to project 1",
  "user": "testuser1"
}
```

**Real-time Notifications:**
- Create bug via Postman → See notification in WebSocket
- Add comment via API → See notification in WebSocket
- Update bug status → See notification in WebSocket

### 🎯 Complete Test Flow

1. ✅ Redis running
2. ✅ Django server with ASGI
3. ✅ Login via Postman (get JWT token)
4. ✅ WebSocket connected in browser
5. ✅ See real-time notification in browser
6. ✅ Add comment via Postman
7. ✅ See real-time comment notification

**Congratulations! Your real-time bug tracking system is fully operational! 🚀**

---

## 📚 Additional Resources

- **API Documentation:** `http://localhost:8000/swagger/`
- **Admin Interface:** `http://localhost:8000/admin/`
- **Django Channels Docs:** https://channels.readthedocs.io/
- **DRF Documentation:** https://www.django-rest-framework.org/
- **Redis Documentation:** https://redis.io/documentation
