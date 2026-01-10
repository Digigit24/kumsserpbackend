"""
Long polling views for real-time communication.
Replaces SSE with long polling approach.
"""
import json
import logging
import time
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .redis_pubsub import (
    get_redis,
    set_user_online,
    set_user_offline,
)

logger = logging.getLogger(__name__)
User = get_user_model()

# Long polling timeout in seconds
LONG_POLLING_TIMEOUT = 5.5
# Check interval in seconds
CHECK_INTERVAL = 0.3


def get_user_from_token(request):
    """
    Authenticate user from token in query params or Authorization header.

    Args:
        request: Django request object

    Returns:
        User object or None
    """
    # Try query parameter first
    token_key = request.GET.get('token')

    # Try Authorization header
    if not token_key:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.replace('Token ', '')
        elif auth_header.startswith('Bearer '):
            token_key = auth_header.replace('Bearer ', '')

    if not token_key:
        return None

    try:
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        logger.warning(f"Invalid token: {token_key[:10]}...")
        return None


def get_user_event_queue_key(user_id):
    """Get Redis key for user's event queue."""
    return f"event_queue:user:{user_id}"


def get_college_event_queue_key(college_id):
    """Get Redis key for college's event queue."""
    return f"event_queue:college:{college_id}"


def get_pending_events(redis_client, user_id, college_id=None):
    """
    Get all pending events for a user from Redis queues.

    Args:
        redis_client: Redis client instance
        user_id: ID of the user
        college_id: Optional college ID for college-wide events

    Returns:
        list: List of events
    """
    events = []

    # Get user-specific events
    user_queue_key = get_user_event_queue_key(user_id)

    # Get all events from the queue (non-blocking)
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


@require_http_methods(["GET"])
def long_poll_events(request):
    """
    Long polling endpoint for real-time events.

    This endpoint will:
    1. Check for pending events immediately
    2. If events exist, return them immediately
    3. If no events, wait up to 5-6 seconds checking periodically
    4. Return empty response if timeout is reached
    5. Client should immediately make a new request

    URL: /api/v1/communication/poll/events/?token=YOUR_TOKEN

    Returns:
        JsonResponse: Events or empty list
    """
    # Authenticate user
    user = get_user_from_token(request)

    if not user or not user.is_authenticated:
        return JsonResponse({
            'error': 'Unauthorized',
            'events': []
        }, status=401)

    redis_client = get_redis()
    if not redis_client:
        return JsonResponse({
            'error': 'Redis not available',
            'events': []
        }, status=503)

    # Mark user as online
    set_user_online(user.id, ttl=300)

    # Get college ID if available
    college_id = getattr(user, 'college_id', None)

    # Start time for timeout
    start_time = time.time()

    # Long polling loop
    while True:
        # Check for pending events
        events = get_pending_events(redis_client, user.id, college_id)

        # If we have events, return them immediately
        if events:
            # Refresh online status
            set_user_online(user.id, ttl=300)

            logger.debug(f"Returning {len(events)} events to user {user.id}")
            return JsonResponse({
                'events': events,
                'timestamp': time.time()
            })

        # Check if timeout reached
        elapsed = time.time() - start_time
        if elapsed >= LONG_POLLING_TIMEOUT:
            # Refresh online status before timeout
            set_user_online(user.id, ttl=300)

            logger.debug(f"Long poll timeout for user {user.id}")
            return JsonResponse({
                'events': [],
                'timestamp': time.time()
            })

        # Wait before next check
        time.sleep(CHECK_INTERVAL)


@require_http_methods(["GET"])
def poll_test(request):
    """
    Test long polling endpoint to verify it's working.

    URL: /api/v1/communication/poll/test/

    Returns:
        JsonResponse: Test response
    """
    # Simulate waiting
    time.sleep(1)

    return JsonResponse({
        'status': 'ok',
        'message': 'Long polling is working',
        'timestamp': time.time()
    })


@require_http_methods(["POST"])
def disconnect(request):
    """
    Endpoint to manually mark user as offline.

    URL: /api/v1/communication/poll/disconnect/?token=YOUR_TOKEN

    Returns:
        JsonResponse: Success response
    """
    user = get_user_from_token(request)

    if not user or not user.is_authenticated:
        return JsonResponse({
            'error': 'Unauthorized'
        }, status=401)

    # Mark user as offline
    set_user_offline(user.id)

    logger.info(f"User {user.id} disconnected")

    return JsonResponse({
        'status': 'disconnected',
        'user_id': user.id
    })
