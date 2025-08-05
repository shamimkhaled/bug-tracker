import logging
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
from urllib.parse import parse_qs
from http.cookies import SimpleCookie

logger = logging.getLogger(__name__)

class WebSocketAuthMiddleware:
    """
     WebSocket authentication middleware that handles session cookies properly
    """
    
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        logger.info("[MIDDLEWARE] WebSocket Auth Middleware called")
        
        # Default to anonymous user
        scope['user'] = AnonymousUser()
        scope['session'] = {}
        
        # Debug: Print all headers
        headers = dict(scope.get('headers', []))
        logger.info(f"[MIDDLEWARE] Headers: {list(headers.keys())}")
        
        
        
        # Try query string method first (your working method)
        session_key = self.get_session_from_query(scope)
        if session_key:
            logger.info(f"[MIDDLEWARE] Found session in query: {session_key[:20]}...")
            user = await self.get_user_from_session_key(session_key)
            if user and not isinstance(user, AnonymousUser):
                scope['user'] = user
                logger.info(f" [MIDDLEWARE] Query auth successful: {user.username}")
                return await self.app(scope, receive, send)
            
            
        
        # Try cookie method
        session_key = self.get_session_from_cookies(scope)
        if session_key:
            logger.info(f"[MIDDLEWARE] Found session in cookies: {session_key[:20]}...")
            user = await self.get_user_from_session_key(session_key)
            if user and not isinstance(user, AnonymousUser):
                scope['user'] = user
                logger.info(f" [MIDDLEWARE] Cookie auth successful: {user.username}")
                return await self.app(scope, receive, send)
        
        logger.warning(" [MIDDLEWARE] No valid authentication found")
        return await self.app(scope, receive, send)
    
    

    def get_session_from_query(self, scope):
        """Get session key from query string"""
        try:
            query_string = scope.get('query_string', b'').decode()
            if query_string:
                params = parse_qs(query_string)
                session_key = params.get('session_key', [None])[0]
                if session_key:
                    logger.info(f"[MIDDLEWARE] Query session key: {session_key[:10]}...")
                    return session_key
        except Exception as e:
            logger.error(f"[MIDDLEWARE] Query parsing error: {e}")
        return None
    
    
    

    def get_session_from_cookies(self, scope):
        """Get session key from cookies"""
        try:
            headers = dict(scope.get('headers', []))
            
            if b'cookie' in headers:
                cookie_header = headers[b'cookie'].decode()
                logger.info(f" [MIDDLEWARE] Cookie header: {cookie_header}")
                
                # Parse cookies manually (more reliable)
                cookies = {}
                for item in cookie_header.split(';'):
                    if '=' in item:
                        key, value = item.strip().split('=', 1)
                        cookies[key] = value
                
                session_key = cookies.get('sessionid')
                if session_key:
                    logger.info(f"[MIDDLEWARE] Found sessionid: {session_key[:10]}...")
                    return session_key
                else:
                    logger.warning(f" [MIDDLEWARE] No sessionid in cookies: {list(cookies.keys())}")
            else:
                logger.warning(" [MIDDLEWARE] No cookie header found")
                
        except Exception as e:
            logger.error(f"[MIDDLEWARE] Cookie parsing error: {e}")
        return None
    
    
    
    

    @database_sync_to_async
    def get_user_from_session_key(self, session_key):
        """Get user from session key"""
        try:
            logger.info(f"[MIDDLEWARE] Looking up session: {session_key[:10]}...")
            
            # Load session
            session_store = SessionStore(session_key)
            
            if not session_store.exists(session_key):
                logger.warning(f" [MIDDLEWARE] Session does not exist: {session_key[:10]}...")
                return AnonymousUser()
            
            # Load session data
            session_store.load()
            user_id = session_store.get('_auth_user_id')
            
            if not user_id:
                logger.warning(" [MIDDLEWARE] No user ID in session")
                return AnonymousUser()
            
            logger.info(f"[MIDDLEWARE] Found user ID: {user_id}")
            
            # Get user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(pk=user_id)
            
            logger.info(f"[MIDDLEWARE] Loaded user: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"[MIDDLEWARE] User lookup error: {e}")
            return AnonymousUser()
        
        


def WebSocketAuthMiddlewareStack(inner):
    """Middleware stack wrapper"""
    return WebSocketAuthMiddleware(inner)