"""
Redis Pub/Sub utilities for real-time messaging.
Replaces WebSocket with Server-Sent Events (SSE) + Redis.
"""
import json
import logging
import redis
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


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


def publish_event(channel: str, event_type: str, data: Dict[str, Any]) -> bool:
    """
    Publish an event to a Redis channel.

    Args:
        channel: Redis channel name (e.g., 'user:123', 'conversation:456')
        event_type: Type of event (e.g., 'message', 'typing', 'read', 'notification')
        data: Event data to publish

    Returns:
        bool: True if published successfully, False otherwise
    """
    redis_client = get_redis()
    if not redis_client:
        logger.warning(f"Redis not available, cannot publish to {channel}")
        return False

    try:
        message = {
            'event': event_type,
            'data': data
        }
        redis_client.publish(channel, json.dumps(message))
        logger.debug(f"Published {event_type} to {channel}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish to {channel}: {e}")
        return False


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


def subscribe_to_user_events(user_id: int):
    """
    Subscribe to events for a specific user.
    Returns a pubsub object that can be used to listen for events.

    Args:
        user_id: ID of the user to subscribe to

    Returns:
        redis.client.PubSub: PubSub object for listening to events
    """
    redis_client = get_redis()
    if not redis_client:
        return None

    try:
        pubsub = redis_client.pubsub()
        channel = f"user:{user_id}"
        pubsub.subscribe(channel)
        logger.info(f"Subscribed to {channel}")
        return pubsub
    except Exception as e:
        logger.error(f"Failed to subscribe to user:{user_id}: {e}")
        return None


def subscribe_to_college_events(college_id: int):
    """
    Subscribe to events for a specific college.

    Args:
        college_id: ID of the college to subscribe to

    Returns:
        redis.client.PubSub: PubSub object for listening to events
    """
    redis_client = get_redis()
    if not redis_client:
        return None

    try:
        pubsub = redis_client.pubsub()
        channel = f"college:{college_id}"
        pubsub.subscribe(channel)
        logger.info(f"Subscribed to {channel}")
        return pubsub
    except Exception as e:
        logger.error(f"Failed to subscribe to college:{college_id}: {e}")
        return None


def listen_for_events(pubsub, timeout: Optional[int] = None):
    """
    Generator that yields events from a pubsub subscription.

    Args:
        pubsub: Redis pubsub object
        timeout: Timeout in seconds (None for blocking)

    Yields:
        dict: Event data
    """
    if not pubsub:
        return

    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    yield data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                    continue
    except Exception as e:
        logger.error(f"Error listening for events: {e}")
    finally:
        try:
            pubsub.close()
        except:
            pass


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
