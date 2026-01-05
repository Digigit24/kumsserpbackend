import logging
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(token_key):
    try:
        # Handle "Bearer <token>" format if sent
        if token_key.startswith('Bearer '):
            token_key = token_key[7:]
        
        token_key = token_key.strip()
        logger.debug(f"Attempting WebSocket authentication with token: {token_key[:10]}...")
        
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        logger.warning("WebSocket authentication failed: Invalid token")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections via a token in the query string.
    Example: ws://.../?token=YOUR_TOKEN
    """
    async def __call__(self, scope, receive, send):
        try:
            query_string = scope.get("query_string", b"").decode("utf-8")
            query_params = parse_qs(query_string)
            token_key = query_params.get("token", [None])[0]
            
            if token_key:
                scope["user"] = await get_user(token_key)
            elif "user" not in scope:
                scope["user"] = AnonymousUser()
        except Exception as e:
            logger.error(f"TokenAuthMiddleware error: {str(e)}")
            scope["user"] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
