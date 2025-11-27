# backend/direct_chat/middleware.py
"""
Custom middleware to authenticate WebSocket connections using JWT tokens.
"""

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from users.models import CustomUser
from urllib.parse import parse_qs
import logging

logger = logging.getLogger('direct_chat')


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware to authenticate WebSocket connections using JWT tokens from query params.
    """
    
    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            try:
                # Validate token
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Get user from database
                scope['user'] = await self.get_user(user_id)
                logger.info(f"WebSocket authenticated: {scope['user'].username}")
                
            except TokenError as e:
                logger.warning(f"Invalid token: {e}")
                scope['user'] = AnonymousUser()
            except Exception as e:
                logger.error(f"Auth error: {e}")
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return AnonymousUser()


def JWTAuthMiddlewareStack(inner):
    """
    Wrapper function to apply JWT authentication middleware.
    """
    return JWTAuthMiddleware(inner)