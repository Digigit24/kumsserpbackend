"""
WebSocket authentication middleware.
Authenticates WebSocket connections using token authentication.
"""
import logging
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token_key):
    """
    Get user from authentication token.

    Args:
        token_key: Authentication token string

    Returns:
        User: User object or AnonymousUser if authentication fails
    """
    try:
        # Handle "Bearer <token>" format if sent
        if token_key.startswith('Bearer '):
            token_key = token_key[7:]
        elif token_key.startswith('Token '):
            token_key = token_key[6:]

        token_key = token_key.strip()

        # Authenticate via token
        token = Token.objects.select_related('user').get(key=token_key)
        user = token.user

        if user.is_active:
            logger.debug(f"WebSocket authenticated: user_id={user.id}, username={user.username}")
            return user
        else:
            logger.warning(f"WebSocket authentication failed: User {user.id} is inactive")
            return AnonymousUser()

    except Token.DoesNotExist:
        logger.warning(f"WebSocket authentication failed: Invalid token {token_key[:10]}...")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}", exc_info=True)
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections via token.

    Supports token in:
    - Query parameter: ws://.../?token=YOUR_TOKEN
    - Authorization header: Authorization: Token YOUR_TOKEN

    Usage:
        application = TokenAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    """

    async def __call__(self, scope, receive, send):
        """
        Authenticate WebSocket connection.

        Args:
            scope: ASGI connection scope
            receive: ASGI receive callable
            send: ASGI send callable

        Returns:
            ASGI response
        """
        try:
            # Get token from query parameters
            query_string = scope.get("query_string", b"").decode("utf-8")
            query_params = parse_qs(query_string)
            token_key = query_params.get("token", [None])[0]

            # If not in query params, check headers
            if not token_key:
                headers = dict(scope.get("headers", []))
                auth_header = headers.get(b"authorization", b"").decode("utf-8")

                if auth_header:
                    token_key = auth_header

            # Authenticate user
            if token_key:
                scope["user"] = await get_user_from_token(token_key)
            else:
                logger.debug("WebSocket: No authentication token provided")
                scope["user"] = AnonymousUser()

        except Exception as e:
            logger.error(f"TokenAuthMiddleware error: {e}", exc_info=True)
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)


class WebSocketRateLimitMiddleware(BaseMiddleware):
    """
    Rate limiting middleware for WebSocket connections.
    Prevents abuse by limiting connection attempts per IP.

    Note: Requires Redis for distributed rate limiting.
    """

    MAX_CONNECTIONS_PER_IP = 10
    MAX_MESSAGES_PER_MINUTE = 60

    async def __call__(self, scope, receive, send):
        """
        Check rate limits before allowing WebSocket connection.

        Args:
            scope: ASGI connection scope
            receive: ASGI receive callable
            send: ASGI send callable

        Returns:
            ASGI response or closes connection if rate limit exceeded
        """
        # Get client IP
        client_ip = scope.get("client", ["unknown", 0])[0]

        # Check connection rate limit
        if not await self.check_connection_limit(client_ip):
            logger.warning(f"WebSocket rate limit exceeded for IP: {client_ip}")
            # Close connection with rate limit error
            await send({
                "type": "websocket.close",
                "code": 4029  # Custom code for rate limit
            })
            return

        return await super().__call__(scope, receive, send)

    async def check_connection_limit(self, client_ip):
        """
        Check if IP has exceeded connection limit.

        Args:
            client_ip: Client IP address

        Returns:
            bool: True if within limit, False otherwise
        """
        try:
            from .redis_utils import get_redis_client

            client = get_redis_client()
            if not client:
                # If Redis unavailable, allow connection
                return True

            key = f"ws:ratelimit:conn:{client_ip}"
            count = client.incr(key)

            if count == 1:
                # Set expiry on first increment
                client.expire(key, 60)  # 1 minute window

            return count <= self.MAX_CONNECTIONS_PER_IP

        except Exception as e:
            logger.error(f"Error checking connection limit: {e}")
            # Allow connection on error
            return True


class WebSocketLoggingMiddleware(BaseMiddleware):
    """
    Logging middleware for WebSocket connections.
    Logs connection/disconnection events for monitoring.
    """

    async def __call__(self, scope, receive, send):
        """
        Log WebSocket connection events.

        Args:
            scope: ASGI connection scope
            receive: ASGI receive callable
            send: ASGI send callable

        Returns:
            ASGI response
        """
        # Log connection attempt
        user = scope.get("user", "unknown")
        path = scope.get("path", "unknown")
        client_ip = scope.get("client", ["unknown", 0])[0]

        user_id = getattr(user, 'id', 'anonymous')
        username = getattr(user, 'username', 'anonymous')

        logger.info(
            f"WebSocket CONNECT: path={path}, user_id={user_id}, "
            f"username={username}, ip={client_ip}"
        )

        # Wrap send to log disconnection
        original_send = send

        async def logging_send(message):
            if message.get("type") == "websocket.close":
                code = message.get("code", "unknown")
                logger.info(
                    f"WebSocket DISCONNECT: path={path}, user_id={user_id}, "
                    f"username={username}, code={code}"
                )
            await original_send(message)

        return await super().__call__(scope, receive, logging_send)
