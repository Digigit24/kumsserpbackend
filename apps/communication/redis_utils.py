"""
Redis utilities for WebSocket real-time features.
Handles presence (online/offline), typing indicators, and caching.
"""
import logging
import redis
from django.conf import settings
from typing import Set, Optional

logger = logging.getLogger(__name__)

# Redis client singleton
_redis_client = None


def get_redis_client():
    """
    Get or create Redis client instance.

    Returns:
        redis.Redis: Redis client instance or None if connection fails
    """
    global _redis_client

    if _redis_client is None:
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379')
            _redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            _redis_client.ping()
            logger.info(f"Redis client initialized: {redis_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            _redis_client = None

    return _redis_client


def is_redis_available():
    """
    Check if Redis is available.

    Returns:
        bool: True if Redis is available, False otherwise
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")
        return False


# Online/Offline Status Management

def set_user_online_ws(user_id: int, ttl: int = 300) -> bool:
    """
    Mark a user as online for WebSocket connections.

    Args:
        user_id: User ID
        ttl: Time to live in seconds (default: 5 minutes)

    Returns:
        bool: True if successful, False otherwise
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        # Add to online users set
        client.sadd('ws:online_users', user_id)

        # Set individual online key with TTL for auto-cleanup
        client.setex(f'ws:online:{user_id}', ttl, '1')

        logger.debug(f"User {user_id} marked online (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.error(f"Error setting user {user_id} online: {e}")
        return False


def set_user_offline_ws(user_id: int) -> bool:
    """
    Mark a user as offline.

    Args:
        user_id: User ID

    Returns:
        bool: True if successful, False otherwise
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        # Remove from online users set
        client.srem('ws:online_users', user_id)

        # Remove online key
        client.delete(f'ws:online:{user_id}')

        logger.debug(f"User {user_id} marked offline")
        return True
    except Exception as e:
        logger.error(f"Error setting user {user_id} offline: {e}")
        return False


def is_user_online_ws(user_id: int) -> bool:
    """
    Check if a user is currently online.

    Args:
        user_id: User ID

    Returns:
        bool: True if user is online, False otherwise
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        return client.exists(f'ws:online:{user_id}') > 0
    except Exception as e:
        logger.error(f"Error checking if user {user_id} is online: {e}")
        return False


def get_online_users_ws() -> Set[int]:
    """
    Get set of all online user IDs.

    Returns:
        Set[int]: Set of online user IDs
    """
    client = get_redis_client()
    if not client:
        return set()

    try:
        online_users = client.smembers('ws:online_users')
        return {int(uid) for uid in online_users}
    except Exception as e:
        logger.error(f"Error getting online users: {e}")
        return set()


def get_online_count_ws() -> int:
    """
    Get count of online users.

    Returns:
        int: Number of online users
    """
    client = get_redis_client()
    if not client:
        return 0

    try:
        return client.scard('ws:online_users')
    except Exception as e:
        logger.error(f"Error getting online user count: {e}")
        return 0


def refresh_user_online_ws(user_id: int, ttl: int = 300) -> bool:
    """
    Refresh user's online status TTL (keep-alive).

    Args:
        user_id: User ID
        ttl: New TTL in seconds

    Returns:
        bool: True if successful, False otherwise
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        if client.exists(f'ws:online:{user_id}'):
            client.expire(f'ws:online:{user_id}', ttl)
            return True
        return False
    except Exception as e:
        logger.error(f"Error refreshing online status for user {user_id}: {e}")
        return False


# Typing Indicators Cache

def set_typing_indicator(user_id: int, partner_id: int, is_typing: bool, ttl: int = 5) -> bool:
    """
    Set typing indicator in Redis cache.

    Args:
        user_id: ID of user who is typing
        partner_id: ID of conversation partner
        is_typing: True if typing, False if stopped
        ttl: Time to live in seconds (default: 5 seconds)

    Returns:
        bool: True if successful
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        key = f'ws:typing:{user_id}:{partner_id}'
        if is_typing:
            client.setex(key, ttl, '1')
        else:
            client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Error setting typing indicator: {e}")
        return False


def is_user_typing(user_id: int, partner_id: int) -> bool:
    """
    Check if user is typing to partner.

    Args:
        user_id: ID of user who might be typing
        partner_id: ID of conversation partner

    Returns:
        bool: True if user is typing
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        key = f'ws:typing:{user_id}:{partner_id}'
        return client.exists(key) > 0
    except Exception as e:
        logger.error(f"Error checking typing indicator: {e}")
        return False


# Message Delivery Tracking

def cache_pending_message(user_id: int, message_data: dict, ttl: int = 86400) -> bool:
    """
    Cache a pending message for offline users.

    Args:
        user_id: Recipient user ID
        message_data: Message data dictionary
        ttl: Time to live in seconds (default: 24 hours)

    Returns:
        bool: True if successful
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        import json
        key = f'ws:pending:{user_id}'
        client.lpush(key, json.dumps(message_data))
        client.expire(key, ttl)
        return True
    except Exception as e:
        logger.error(f"Error caching pending message: {e}")
        return False


def get_pending_messages(user_id: int) -> list:
    """
    Get and clear pending messages for a user.

    Args:
        user_id: User ID

    Returns:
        list: List of pending message dictionaries
    """
    client = get_redis_client()
    if not client:
        return []

    try:
        import json
        key = f'ws:pending:{user_id}'
        messages = []

        # Get all messages
        while True:
            msg_json = client.rpop(key)
            if not msg_json:
                break
            try:
                messages.append(json.loads(msg_json))
            except json.JSONDecodeError:
                continue

        return messages
    except Exception as e:
        logger.error(f"Error getting pending messages: {e}")
        return []


# Unread Count Caching

def increment_unread_count(user_id: int, conversation_id: int) -> Optional[int]:
    """
    Increment unread count for a conversation in cache.

    Args:
        user_id: User ID
        conversation_id: Conversation ID

    Returns:
        Optional[int]: New unread count or None on error
    """
    client = get_redis_client()
    if not client:
        return None

    try:
        key = f'ws:unread:{user_id}:{conversation_id}'
        return client.incr(key)
    except Exception as e:
        logger.error(f"Error incrementing unread count: {e}")
        return None


def reset_unread_count(user_id: int, conversation_id: int) -> bool:
    """
    Reset unread count for a conversation.

    Args:
        user_id: User ID
        conversation_id: Conversation ID

    Returns:
        bool: True if successful
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        key = f'ws:unread:{user_id}:{conversation_id}'
        client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Error resetting unread count: {e}")
        return False


def get_unread_count(user_id: int, conversation_id: int) -> int:
    """
    Get unread count for a conversation.

    Args:
        user_id: User ID
        conversation_id: Conversation ID

    Returns:
        int: Unread count
    """
    client = get_redis_client()
    if not client:
        return 0

    try:
        key = f'ws:unread:{user_id}:{conversation_id}'
        count = client.get(key)
        return int(count) if count else 0
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return 0


# Connection Tracking

def track_websocket_connection(user_id: int, connection_id: str) -> bool:
    """
    Track a WebSocket connection for a user.

    Args:
        user_id: User ID
        connection_id: Unique connection identifier

    Returns:
        bool: True if successful
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        key = f'ws:connections:{user_id}'
        client.sadd(key, connection_id)
        client.expire(key, 3600)  # 1 hour expiry
        return True
    except Exception as e:
        logger.error(f"Error tracking connection: {e}")
        return False


def remove_websocket_connection(user_id: int, connection_id: str) -> bool:
    """
    Remove a WebSocket connection tracking.

    Args:
        user_id: User ID
        connection_id: Connection identifier

    Returns:
        bool: True if successful
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        key = f'ws:connections:{user_id}'
        client.srem(key, connection_id)

        # If no more connections, mark user offline
        if client.scard(key) == 0:
            set_user_offline_ws(user_id)

        return True
    except Exception as e:
        logger.error(f"Error removing connection: {e}")
        return False


def get_user_connection_count(user_id: int) -> int:
    """
    Get number of active WebSocket connections for a user.

    Args:
        user_id: User ID

    Returns:
        int: Number of active connections
    """
    client = get_redis_client()
    if not client:
        return 0

    try:
        key = f'ws:connections:{user_id}'
        return client.scard(key)
    except Exception as e:
        logger.error(f"Error getting connection count: {e}")
        return 0


# Cleanup utilities

def cleanup_stale_online_users() -> int:
    """
    Clean up stale online users from the set.
    Should be called periodically by a background task.

    Returns:
        int: Number of users cleaned up
    """
    client = get_redis_client()
    if not client:
        return 0

    try:
        online_users = client.smembers('ws:online_users')
        cleaned = 0

        for user_id in online_users:
            # Check if the user's online key still exists
            if not client.exists(f'ws:online:{user_id}'):
                client.srem('ws:online_users', user_id)
                cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} stale online users")

        return cleaned
    except Exception as e:
        logger.error(f"Error cleaning up stale users: {e}")
        return 0


def clear_all_websocket_data() -> bool:
    """
    Clear all WebSocket-related data from Redis.
    USE WITH CAUTION - for testing/maintenance only.

    Returns:
        bool: True if successful
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        # Get all ws: keys
        keys = client.keys('ws:*')
        if keys:
            client.delete(*keys)
            logger.warning(f"Cleared {len(keys)} WebSocket keys from Redis")
        return True
    except Exception as e:
        logger.error(f"Error clearing WebSocket data: {e}")
        return False
