"""
Redis Pub/Sub utilities for real-time messaging.
Replaces WebSocket with Server-Sent Events (SSE) + Redis.

DEPRECATED: This file is commented out in favor of Node.js WebSocket microservice.
The Redis Pub/Sub implementation has been replaced with Socket.io for better real-time performance.
See: /websocket-service/ directory for the new microservice implementation.

Functions are kept but commented out for reference.
"""
# import json
# import logging
# import redis
# from django.conf import settings
# from typing import Dict, Any, Optional

# logger = logging.getLogger(__name__)


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
        redis_client.publish(channel, json.dumps(message, default=str))
        logger.debug(f"Published {event_type} to {channel}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish to {channel}: {e}")
        return False


# Stub functions that do nothing - replaced by WebSocket microservice
def publish_message_event(receiver_id, message_data):
    """DEPRECATED: Use WebSocket microservice instead"""
    pass

def publish_typing_event(receiver_id, sender_id, sender_name, is_typing):
    """DEPRECATED: Use WebSocket microservice instead"""
    pass

def publish_read_receipt(sender_id, message_id, reader_id, reader_name):
    """DEPRECATED: Use WebSocket microservice instead"""
    pass

def publish_notification(user_id, notification_data):
    """DEPRECATED: Use WebSocket microservice instead"""
    pass

def publish_college_notification(college_id, notification_data):
    """DEPRECATED: Use WebSocket microservice instead"""
    pass


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


# Stub functions that do nothing - replaced by WebSocket microservice
def get_online_users():
    """DEPRECATED: Use WebSocket microservice instead"""
    return set()

def set_user_online(user_id, ttl=300):
    """DEPRECATED: Use WebSocket microservice instead"""
    return True

def set_user_offline(user_id):
    """DEPRECATED: Use WebSocket microservice instead"""
    return True

def is_user_online(user_id):
    """DEPRECATED: Use WebSocket microservice instead - returns False as stub"""
    return False
