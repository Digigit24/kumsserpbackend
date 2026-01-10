"""
RabbitMQ utilities for real-time messaging with long polling.
Uses RabbitMQ message queues instead of Redis for better cross-platform compatibility.
"""
import json
import logging
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
from django.conf import settings
from typing import Dict, Any, Optional, List
import time

logger = logging.getLogger(__name__)

# Maximum events to keep in queue per user (prevent memory issues)
MAX_QUEUE_SIZE = 100
# Message TTL in milliseconds (30 minutes)
MESSAGE_TTL = 1800000  # 30 minutes in ms
# Online status TTL in seconds
ONLINE_TTL = 300  # 5 minutes


class RabbitMQClient:
    """
    Singleton RabbitMQ client for queue operations.
    """
    _instance = None
    _connection = None
    _channel = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RabbitMQClient, cls).__new__(cls)
            cls._instance._initialize_rabbitmq()
        return cls._instance

    def _initialize_rabbitmq(self):
        """Initialize RabbitMQ connection."""
        try:
            # Get RabbitMQ URL from settings
            rabbitmq_url = getattr(settings, 'RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

            # Parse connection parameters from URL
            parameters = pika.URLParameters(rabbitmq_url)
            parameters.heartbeat = 600
            parameters.blocked_connection_timeout = 300

            # Create connection
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            # Declare exchange for dead letter (expired messages)
            self._channel.exchange_declare(
                exchange='dlx',
                exchange_type='direct',
                durable=True
            )

            logger.info(f"RabbitMQ connected successfully: {rabbitmq_url}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self._connection = None
            self._channel = None

    def get_channel(self):
        """Get RabbitMQ channel instance."""
        if self._connection is None or self._connection.is_closed:
            self._initialize_rabbitmq()

        if self._channel is None or self._channel.is_closed:
            if self._connection and not self._connection.is_closed:
                self._channel = self._connection.channel()

        return self._channel

    def is_connected(self):
        """Check if RabbitMQ is connected."""
        try:
            if self._connection and not self._connection.is_closed:
                if self._channel and not self._channel.is_closed:
                    return True
        except:
            pass
        return False

    def close(self):
        """Close RabbitMQ connection."""
        try:
            if self._channel and not self._channel.is_closed:
                self._channel.close()
            if self._connection and not self._connection.is_closed:
                self._connection.close()
        except:
            pass


def get_rabbitmq():
    """Get RabbitMQ client."""
    return RabbitMQClient()


def ensure_queue_exists(channel, queue_name: str, ttl: int = MESSAGE_TTL):
    """
    Ensure a queue exists with proper configuration.

    Args:
        channel: RabbitMQ channel
        queue_name: Name of the queue
        ttl: Message TTL in milliseconds
    """
    try:
        # Declare queue with message TTL and max length
        channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-message-ttl': ttl,  # Messages expire after TTL
                'x-max-length': MAX_QUEUE_SIZE,  # Max messages in queue
                'x-overflow': 'drop-head',  # Drop oldest messages when full
            }
        )
    except Exception as e:
        logger.error(f"Failed to declare queue {queue_name}: {e}")


def queue_event(queue_key: str, event_type: str, data: Dict[str, Any]) -> bool:
    """
    Add an event to a RabbitMQ queue for long polling.

    Args:
        queue_key: Queue name (e.g., 'event_queue:user:123')
        event_type: Type of event (e.g., 'message', 'typing', 'read', 'notification')
        data: Event data to queue

    Returns:
        bool: True if queued successfully, False otherwise
    """
    client = get_rabbitmq()
    channel = client.get_channel()

    if not channel:
        logger.warning(f"RabbitMQ not available, cannot queue event to {queue_key}")
        return False

    try:
        # Ensure queue exists
        ensure_queue_exists(channel, queue_key)

        message = {
            'event': event_type,
            'data': data,
            'timestamp': data.get('timestamp') or None
        }

        # Publish message to queue
        channel.basic_publish(
            exchange='',
            routing_key=queue_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json',
            )
        )

        logger.debug(f"Queued {event_type} to {queue_key}")
        return True
    except Exception as e:
        logger.error(f"Failed to queue event to {queue_key}: {e}")
        return False


def publish_event(channel: str, event_type: str, data: Dict[str, Any]) -> bool:
    """
    Publish an event to a queue (legacy function for compatibility).
    Converts channel name to queue key format.

    Args:
        channel: Channel name (e.g., 'user:123', 'college:456')
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
    Publish a new message event to the receiver's queue.

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
    Publish a notification to a user's queue.

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
    """Get queue key for a user's events."""
    return f"event_queue:user:{user_id}"


def get_college_event_queue_key(college_id: int) -> str:
    """Get queue key for a college's events."""
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
    client = get_rabbitmq()
    channel = client.get_channel()

    if not channel:
        return []

    events = []

    # Get user-specific events
    user_queue_key = get_user_event_queue_key(user_id)
    ensure_queue_exists(channel, user_queue_key)

    while True:
        try:
            method_frame, header_frame, body = channel.basic_get(
                queue=user_queue_key,
                auto_ack=True
            )

            if method_frame is None:
                # No more messages
                break

            event = json.loads(body)
            events.append(event)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode event: {e}")
            continue
        except Exception as e:
            logger.error(f"Error getting message from queue: {e}")
            break

    # Get college-wide events if college_id is provided
    if college_id:
        college_queue_key = get_college_event_queue_key(college_id)
        ensure_queue_exists(channel, college_queue_key)

        while True:
            try:
                method_frame, header_frame, body = channel.basic_get(
                    queue=college_queue_key,
                    auto_ack=True
                )

                if method_frame is None:
                    # No more messages
                    break

                event = json.loads(body)
                events.append(event)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode college event: {e}")
                continue
            except Exception as e:
                logger.error(f"Error getting message from college queue: {e}")
                break

    return events


def clear_user_event_queue(user_id: int) -> bool:
    """
    Clear all events from a user's queue.

    Args:
        user_id: ID of the user

    Returns:
        bool: True if successful
    """
    client = get_rabbitmq()
    channel = client.get_channel()

    if not channel:
        return False

    try:
        queue_key = get_user_event_queue_key(user_id)
        channel.queue_purge(queue=queue_key)
        return True
    except Exception as e:
        logger.error(f"Failed to clear queue for user {user_id}: {e}")
        return False


# Online status tracking using RabbitMQ queues with TTL
# We'll use a dedicated queue for each user's online status

def get_online_status_queue(user_id: int) -> str:
    """Get queue name for user's online status."""
    return f"online_status:user:{user_id}"


def set_user_online(user_id: int, ttl: int = ONLINE_TTL) -> bool:
    """
    Mark a user as online. Uses RabbitMQ queue with TTL.

    Args:
        user_id: ID of the user
        ttl: Time to live in seconds (default 5 minutes)

    Returns:
        bool: True if successful
    """
    client = get_rabbitmq()
    channel = client.get_channel()

    if not channel:
        return False

    try:
        queue_name = get_online_status_queue(user_id)

        # Declare queue with TTL (in milliseconds)
        channel.queue_declare(
            queue=queue_name,
            durable=False,  # Not persistent for online status
            arguments={
                'x-expires': ttl * 1000,  # Queue auto-deletes after TTL
                'x-max-length': 1,  # Only keep one message
            }
        )

        # Publish a simple status message
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps({'user_id': user_id, 'online': True, 'timestamp': time.time()}),
            properties=pika.BasicProperties(
                expiration=str(ttl * 1000)  # Message expires after TTL
            )
        )

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
    client = get_rabbitmq()
    channel = client.get_channel()

    if not channel:
        return False

    try:
        queue_name = get_online_status_queue(user_id)
        # Delete the queue to mark as offline
        channel.queue_delete(queue=queue_name)
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
    client = get_rabbitmq()
    channel = client.get_channel()

    if not channel:
        return False

    try:
        queue_name = get_online_status_queue(user_id)
        # Check if queue exists by declaring passively
        result = channel.queue_declare(queue=queue_name, passive=True)
        # If queue exists and has messages, user is online
        return result.method.message_count > 0
    except AMQPChannelError:
        # Queue doesn't exist, user is offline
        # Need to reopen channel after passive declare failure
        try:
            client._channel = client._connection.channel()
        except:
            pass
        return False
    except Exception as e:
        logger.error(f"Failed to check if user {user_id} is online: {e}")
        return False


def get_online_users() -> set:
    """
    Get set of currently online user IDs.
    Note: This is expensive with RabbitMQ. Consider caching or alternative approach.

    Returns:
        set: Set of user IDs currently online
    """
    # This is difficult to implement efficiently with RabbitMQ
    # Consider using a database cache or separate tracking system
    logger.warning("get_online_users is expensive with RabbitMQ, consider caching")
    return set()


# Legacy Pub/Sub functions - kept for backward compatibility but not used with long polling

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
