"""
Redis utilities for real-time messaging.
Now uses Redis Lists (queues) for long polling instead of Pub/Sub.
"""
import json
import logging
import redis
from django.conf import settings
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Maximum events to keep in queue per user (prevent memory issues)
MAX_QUEUE_SIZE = 100
# Queue expiration time in seconds (30 minutes)
QUEUE_EXPIRATION = 1800


class RedisClient:
    """
    Singleton Redis client for pub/sub operations.
    """
    _instance = None
    _redis_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialize_redis()
        return cls._instance

    def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379')
            self._redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self._redis_client.ping()
            logger.info(f"Redis connected successfully: {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis_client = None

    def get_client(self):
        """Get Redis client instance."""
        if self._redis_client is None:
            self._initialize_redis()
        return self._redis_client

    def is_connected(self):
        """Check if Redis is connected."""
        try:
            if self._redis_client:
                self._redis_client.ping()
                return True
        except:
            pass
        return False


def get_redis():
    """Get Redis client."""
    return RedisClient().get_client()


def queue_event(queue_key: str, event_type: str, data: Dict[str, Any]) -> bool:
    """
    Add an event to a Redis queue (list) for long polling.

    Args:
        queue_key: Redis queue key (e.g., 'event_queue:user:123')
        event_type: Type of event (e.g., 'message', 'typing', 'read', 'notification')
        data: Event data to queue

    Returns:
        bool: True if queued successfully, False otherwise
    """
    redis_client = get_redis()
    if not redis_client:
        logger.warning(f"Redis not available, cannot queue event to {queue_key}")
        return False

    try:
        message = {
            'event': event_type,
            'data': data,
            'timestamp': data.get('timestamp') or None
        }

        # Add event to queue (right push to end of list)
        redis_client.rpush(queue_key, json.dumps(message))

        # Trim queue to maximum size (keep only last MAX_QUEUE_SIZE events)
        redis_client.ltrim(queue_key, -MAX_QUEUE_SIZE, -1)

        # Set expiration on queue to prevent stale data
        redis_client.expire(queue_key, QUEUE_EXPIRATION)

        logger.debug(f"Queued {event_type} to {queue_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to queue event to {queue_key}: {e}")
        return False


def publish_event(channel: str, event_type: str, data: Dict[str, Any]) -> bool:
    """
    Legacy function - now uses queue_event for long polling.
    Converts channel name to queue key format.

    Args:
        channel: Redis channel name (e.g., 'user:123', 'college:456')
        event_type: Type of event (e.g., 'message', 'typing', 'read', 'notification')
        data: Event data to publish

    Returns:
        bool: True if queued successfully, False otherwise
    """
    # Convert channel to queue key
    queue_key = f"event_queue:{channel}"
    return queue_event(queue_key, event_type, data)


def publish_message_event(receiver_id: int, message_data: Dict[str, Any]) -> bool:
    """
    Publish a new message event to the receiver's channel.

    Args:
        receiver_id: ID of the message receiver
        message_data: Message data including id, sender, content, etc.

    Returns:
        bool: True if published successfully
    """
    channel = f"user:{receiver_id}"
    return publish_event(channel, 'message', message_data)


def publish_typing_event(receiver_id: int, sender_id: int, sender_name: str, is_typing: bool) -> bool:
    """
    Publish a typing indicator event.

    Args:
        receiver_id: ID of the user who should see the typing indicator
        sender_id: ID of the user who is typing
        sender_name: Name of the user who is typing
        is_typing: True if user is typing, False if stopped

    Returns:
        bool: True if published successfully
    """
    channel = f"user:{receiver_id}"
    data = {
        'sender_id': sender_id,
        'sender_name': sender_name,
        'is_typing': is_typing
    }
    return publish_event(channel, 'typing', data)


def publish_read_receipt(sender_id: int, message_id: int, reader_id: int, reader_name: str) -> bool:
    """
    Publish a read receipt to the original message sender.

    Args:
        sender_id: ID of the original message sender
        message_id: ID of the message that was read
        reader_id: ID of the user who read the message
        reader_name: Name of the user who read the message

    Returns:
        bool: True if published successfully
    """
    channel = f"user:{sender_id}"
    data = {
        'message_id': message_id,
        'reader_id': reader_id,
        'reader_name': reader_name,
        'read_at': None  # Will be set by the caller
    }
    return publish_event(channel, 'read_receipt', data)


def publish_notification(user_id: int, notification_data: Dict[str, Any]) -> bool:
    """
    Publish a notification to a user's channel.

    Args:
        user_id: ID of the user to notify
        notification_data: Notification data

    Returns:
        bool: True if published successfully
    """
    channel = f"user:{user_id}"
    return publish_event(channel, 'notification', notification_data)


def publish_college_notification(college_id: int, notification_data: Dict[str, Any]) -> bool:
    """
    Publish a notification to all users in a college.

    Args:
        college_id: ID of the college
        notification_data: Notification data

    Returns:
        bool: True if published successfully
    """
    channel = f"college:{college_id}"
    return publish_event(channel, 'notification', notification_data)


def get_user_event_queue_key(user_id: int) -> str:
    """Get Redis queue key for a user's events."""
    return f"event_queue:user:{user_id}"


def get_college_event_queue_key(college_id: int) -> str:
    """Get Redis queue key for a college's events."""
    return f"event_queue:college:{college_id}"


def get_queued_events(user_id: int, college_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get all queued events for a user (non-blocking).

    Args:
        user_id: ID of the user
        college_id: Optional college ID for college-wide events

    Returns:
        List of event dictionaries
    """
    redis_client = get_redis()
    if not redis_client:
        return []

    events = []

    # Get user-specific events
    user_queue_key = get_user_event_queue_key(user_id)
    while True:
        event_data = redis_client.lpop(user_queue_key)
        if not event_data:
            break
        try:
            event = json.loads(event_data)
            events.append(event)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode event: {e}")
            continue

    # Get college-wide events if college_id is provided
    if college_id:
        college_queue_key = get_college_event_queue_key(college_id)
        while True:
            event_data = redis_client.lpop(college_queue_key)
            if not event_data:
                break
            try:
                event = json.loads(event_data)
                events.append(event)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode college event: {e}")
                continue

    return events


def clear_user_event_queue(user_id: int) -> bool:
    """
    Clear all events from a user's queue.

    Args:
        user_id: ID of the user

    Returns:
        bool: True if successful
    """
    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        queue_key = get_user_event_queue_key(user_id)
        redis_client.delete(queue_key)
        return True
    except Exception as e:
        logger.error(f"Failed to clear queue for user {user_id}: {e}")
        return False


# Legacy Pub/Sub functions - kept for backward compatibility but not used with long polling
# These are commented out as they're replaced by queue-based approach

def subscribe_to_user_events(user_id: int):
    """
    DEPRECATED: Legacy function for SSE pub/sub approach.
    Not used with long polling. Kept for backward compatibility.
    """
    logger.warning("subscribe_to_user_events is deprecated with long polling")
    return None


def subscribe_to_college_events(college_id: int):
    """
    DEPRECATED: Legacy function for SSE pub/sub approach.
    Not used with long polling. Kept for backward compatibility.
    """
    logger.warning("subscribe_to_college_events is deprecated with long polling")
    return None


def listen_for_events(pubsub, timeout: Optional[int] = None):
    """
    DEPRECATED: Legacy function for SSE pub/sub approach.
    Not used with long polling. Kept for backward compatibility.
    """
    logger.warning("listen_for_events is deprecated with long polling")
    return
    yield  # Make it a generator to avoid breaking existing code


def get_online_users() -> set:
    """
    Get set of currently online user IDs from Redis.
    Uses a Redis SET to track online users.

    Returns:
        set: Set of user IDs currently online
    """
    redis_client = get_redis()
    if not redis_client:
        return set()

    try:
        return {int(uid) for uid in redis_client.smembers('online_users')}
    except Exception as e:
        logger.error(f"Failed to get online users: {e}")
        return set()


def set_user_online(user_id: int, ttl: int = 300) -> bool:
    """
    Mark a user as online. Uses Redis SET with TTL.

    Args:
        user_id: ID of the user
        ttl: Time to live in seconds (default 5 minutes)

    Returns:
        bool: True if successful
    """
    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        # Add to online users set
        redis_client.sadd('online_users', user_id)
        # Set a key with TTL for auto-cleanup
        redis_client.setex(f'online:user:{user_id}', ttl, '1')
        return True
    except Exception as e:
        logger.error(f"Failed to set user {user_id} online: {e}")
        return False


def set_user_offline(user_id: int) -> bool:
    """
    Mark a user as offline.

    Args:
        user_id: ID of the user

    Returns:
        bool: True if successful
    """
    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        redis_client.srem('online_users', user_id)
        redis_client.delete(f'online:user:{user_id}')
        return True
    except Exception as e:
        logger.error(f"Failed to set user {user_id} offline: {e}")
        return False


def is_user_online(user_id: int) -> bool:
    """
    Check if a user is currently online.

    Args:
        user_id: ID of the user

    Returns:
        bool: True if user is online
    """
    redis_client = get_redis()
    if not redis_client:
        return False

    try:
        return redis_client.exists(f'online:user:{user_id}') > 0
    except Exception as e:
        logger.error(f"Failed to check if user {user_id} is online: {e}")
        return False
