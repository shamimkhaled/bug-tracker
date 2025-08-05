import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser



# class ProjectConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.project_id = self.scope['url_route']['kwargs']['project_id']
#         self.project_group_name = f'project_{self.project_id}'
#         self.user = self.scope["user"]
        
#         # Check if user is authenticated
#         if not self.user.is_authenticated:
#             await self.close()
#             return
        
#         # Check if user has access to this project
#         if not await self.user_has_project_access():
#             await self.close()
#             return
        
#         # Join project group
#         await self.channel_layer.group_add(
#             self.project_group_name,
#             self.channel_name
#         )
        
#         # Join personal user group for direct notifications
#         self.user_group_name = f'user_{self.user.id}'
#         await self.channel_layer.group_add(
#             self.user_group_name,
#             self.channel_name
#         )
        
#         await self.accept()
        
#         # Send connection confirmation
#         # await self.send(text_data=json.dumps({
#         #     'type': 'connection_established',
#         #     'message': f'Connected to project {self.project_id}',
#         #     'user': self.user.username
#         # }))
        
#         await self.send(text_data=json.dumps({
#             'type': 'connection_established',
#             'message': f'Connected to project {self.project_id}',
#             'user': self.user.username if self.user.is_authenticated else 'anonymous'
#         }))
    
#     async def disconnect(self, close_code):
#         # Leave project group
#         await self.channel_layer.group_discard(
#             self.project_group_name,
#             self.channel_name
#         )
        
#         # Leave user group
#         if hasattr(self, 'user_group_name'):
#             await self.channel_layer.group_discard(
#                 self.user_group_name,
#                 self.channel_name
#             )
    
#     async def receive(self, text_data):
#         try:
#             text_data_json = json.loads(text_data)
#             message_type = text_data_json.get('type')
            
#             if message_type == 'typing_indicator':
#                 # Handle typing indicator
#                 await self.channel_layer.group_send(
#                     self.project_group_name,
#                     {
#                         'type': 'typing_notification',
#                         'user': self.user.username,
#                         'is_typing': text_data_json.get('is_typing', False),
#                         'bug_id': text_data_json.get('bug_id'),
#                     }
#                 )
#             elif message_type == 'ping':
#                 # Handle ping for connection health check
#                 await self.send(text_data=json.dumps({
#                     'type': 'pong',
#                     'timestamp': text_data_json.get('timestamp')
#                 }))
        
#         except json.JSONDecodeError:
#             await self.send(text_data=json.dumps({
#                 'type': 'error',
#                 'message': 'Invalid JSON format'
#             }))
    
#     # Receive message from project group
#     async def bug_notification(self, event):
#         await self.send(text_data=json.dumps({
#             'type': 'bug_notification',
#             'event_type': event['event_type'],
#             'bug': event.get('bug', {}),
#             'user': event['user'],
#             'timestamp': str(event.get('timestamp', '')),
#         }))
    
#     async def comment_notification(self, event):
#         await self.send(text_data=json.dumps({
#             'type': 'comment_notification',
#             'comment': event.get('comment', {}),
#             'bug': event.get('bug', {}),
#             'user': event['user'],
#         }))
    
#     async def personal_notification(self, event):
#         await self.send(text_data=json.dumps({
#             'type': 'personal_notification',
#             'notification_type': event['notification_type'],
#             'comment': event.get('comment'),
#             'bug': event.get('bug'),
#             'commenter': event.get('commenter'),
#         }))
    
#     async def typing_notification(self, event):
#         # Don't send typing indicator to the sender
#         if event['user'] != self.user.username:
#             await self.send(text_data=json.dumps({
#                 'type': 'typing_indicator',
#                 'user': event['user'],
#                 'is_typing': event['is_typing'],
#                 'bug_id': event.get('bug_id'),
#             }))
    
#     async def activity_log_update(self, event):
#         await self.send(text_data=json.dumps({
#             'type': 'activity_log_update',
#             'activity': event['activity'],
#         }))
    
#     # @database_sync_to_async
#     # def user_has_project_access(self):
#     #     """Check if user has access to the project"""
#     #     # Import Django models inside the async function to avoid early import issues
#     #     from django.contrib.auth.models import User
#     #     from .models import Project
        
#     #     try:
#     #         project = Project.objects.get(id=self.project_id)
#     #         return (
#     #             project.owner == self.user or 
#     #             project.bugs.filter(assigned_to=self.user).exists() or
#     #             project.bugs.filter(created_by=self.user).exists()
#     #         )
#     #     except Project.DoesNotExist:
#     #         return False
    
    

logger = logging.getLogger(__name__)

class ProjectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("=== WebSocket connection attempt ===")
        
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_group_name = f'project_{self.project_id}'
        self.user = self.scope.get("user")
        
        logger.info(f"Project ID: {self.project_id}")
        logger.info(f"User: {self.user}")
        logger.info(f"User type: {type(self.user)}")
        logger.info(f"User authenticated: {self.user.is_authenticated if hasattr(self.user, 'is_authenticated') else 'No auth method'}")
        
        
        # Check authentication
        if not self.user or isinstance(self.user, AnonymousUser) or not self.user.is_authenticated:
            logger.warning(" User not authenticated")
            
            
            # Try to get user from session
            session = self.scope.get("session", {})
            user_id = session.get("_auth_user_id")
            
            if user_id:
                logger.info(f"Found user ID in session: {user_id}")
                try:
                    from django.contrib.auth.models import User
                    self.user = await database_sync_to_async(User.objects.get)(id=user_id)
                    logger.info(f" Retrieved user from session: {self.user.username}")
                except User.DoesNotExist:
                    logger.warning(" User from session not found")
                    await self.close(code=4001)
                    return
            else:
                logger.warning(" No user in session")
                await self.close(code=4001)
                return
            
        
        # Accept connection
        await self.accept()
        logger.info(f" User {self.user.username} authenticated")
        
        
        # Join project group
        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )
        
        
        # Join personal user group for direct notifications
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        logger.info(f" User {self.user.username} joined groups: {self.project_group_name}, {self.user_group_name}")
        
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to project {self.project_id}',
            'user': self.user.username,
            'project_id': self.project_id,
            'timestamp': str(self._get_current_time())
        }))
        
        logger.info(" Welcome message sent")
        
        
    
    async def disconnect(self, close_code):
        logger.info(f"=== WebSocket disconnected: {close_code} ===")
        
        # Leave project group
        if hasattr(self, 'project_group_name'):
            await self.channel_layer.group_discard(
                self.project_group_name,
                self.channel_name
            )
            logger.info(f"Left project group: {self.project_group_name}")
        
        # Leave user group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            logger.info(f"Left user group: {self.user_group_name}")
            
            
            
    
    async def receive(self, text_data):
        logger.info(f"Received message: {text_data}")
        
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp'),
                    'user': self.user.username,
                    'server_time': str(self._get_current_time())
                }))
                logger.info(" Pong sent")
            
            elif message_type == 'typing_indicator':
                # Handle typing indicator
                await self.channel_layer.group_send(
                    self.project_group_name,
                    {
                        'type': 'typing_notification',
                        'user': self.user.username,
                        'is_typing': text_data_json.get('is_typing', False),
                        'bug_id': text_data_json.get('bug_id'),
                    }
                )
                logger.info(f" Typing indicator sent: {text_data_json.get('is_typing')}")
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError as e:
            logger.error(f" JSON decode error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f" Unexpected error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Server error occurred'
            }))
            
            
            
    
    # Message handlers for notifications
    async def bug_notification(self, event):
        logger.info(f"Sending bug notification: {event.get('event_type')}")
        await self.send(text_data=json.dumps({
            'type': 'bug_notification',
            'event_type': event['event_type'],
            'bug': event.get('bug', {}),
            'user': event['user'],
            'timestamp': str(self._get_current_time())
        }))
        
        
    
    async def comment_notification(self, event):
        logger.info(f"Sending comment notification from {event.get('user')}")
        await self.send(text_data=json.dumps({
            'type': 'comment_notification',
            'comment': event.get('comment', {}),
            'bug': event.get('bug', {}),
            'user': event['user'],
            'timestamp': str(self._get_current_time())
        }))
        
        
    
    async def personal_notification(self, event):
        logger.info(f"Sending personal notification: {event.get('notification_type')}")
        await self.send(text_data=json.dumps({
            'type': 'personal_notification',
            'notification_type': event['notification_type'],
            'comment': event.get('comment'),
            'bug': event.get('bug'),
            'commenter': event.get('commenter'),
            'timestamp': str(self._get_current_time())
        }))
        
        
    
    async def typing_notification(self, event):
        # Don't send typing indicator to the sender
        if event['user'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user': event['user'],
                'is_typing': event['is_typing'],
                'bug_id': event.get('bug_id'),
                'timestamp': str(self._get_current_time())
            }))
            logger.info(f"Sent typing indicator for {event['user']}")
            
            
    
    def _get_current_time(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    
    
    
    @database_sync_to_async
    def user_has_project_access(self):
        """Check if user has access to the project"""
        try:
            from .models import Project
            project = Project.objects.get(id=self.project_id)
            return (
                project.owner == self.user or 
                project.bugs.filter(assigned_to=self.user).exists() or
                project.bugs.filter(created_by=self.user).exists()
            )
        except:
            return False


