"""
Server-Sent Events (SSE) views for real-time communication.
Replaces WebSocket with SSE + Redis Pub/Sub.
"""
import json
import logging
import time
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .redis_pubsub import (
    subscribe_to_user_events,
    subscribe_to_college_events,
    set_user_online,
    set_user_offline,
    listen_for_events
)

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_from_token(request):
    """
    Authenticate user from token in query params or Authorization header.

    Args:
        request: Django request object

    Returns:
        User object or None
    """
    # Try query parameter first (for SSE connections)
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


def event_stream_generator(pubsub, user_id, college_id=None):
    """
    Generator that yields SSE-formatted events from Redis pubsub.

    Args:
        pubsub: Redis pubsub object
        user_id: ID of the connected user
        college_id: Optional college ID for college-wide events

    Yields:
        str: SSE-formatted event data
    """
    # Send initial connection success event
    yield f"event: connected\n"
    yield f"data: {json.dumps({'status': 'connected', 'user_id': str(user_id)}, default=str)}\n\n"

    # Mark user as online
    set_user_online(user_id, ttl=300)

    # Send heartbeat every 30 seconds to keep connection alive
    last_heartbeat = time.time()
    HEARTBEAT_INTERVAL = 30

    try:
        for event in listen_for_events(pubsub):
            # Refresh online status
            set_user_online(user_id, ttl=300)

            # Send the event
            event_type = event.get('event', 'message')
            event_data = event.get('data', {})

            yield f"event: {event_type}\n"
            yield f"data: {json.dumps(event_data, default=str)}\n\n"

            # Send heartbeat if needed
            current_time = time.time()
            if current_time - last_heartbeat > HEARTBEAT_INTERVAL:
                yield f"event: heartbeat\n"
                yield f"data: {json.dumps({'timestamp': current_time}, default=str)}\n\n"
                last_heartbeat = current_time

    except GeneratorExit:
        logger.info(f"SSE connection closed for user {user_id}")
    except Exception as e:
        logger.error(f"Error in event stream for user {user_id}: {e}")
    finally:
        # Mark user as offline
        set_user_offline(user_id)

        # Send disconnection event
        try:
            yield f"event: disconnected\n"
            yield f"data: {json.dumps({'status': 'disconnected'}, default=str)}\n\n"
        except:
            pass


@require_http_methods(["GET"])
def sse_events(request):
    """
    SSE endpoint for real-time events.

    URL: /api/v1/communication/sse/events/?token=YOUR_TOKEN

    Returns:
        StreamingHttpResponse: SSE stream of events
    """
    # Authenticate user
    user = get_user_from_token(request)

    if not user or not user.is_authenticated:
        response = StreamingHttpResponse(
            (f"event: error\ndata: {json.dumps({'error': 'Unauthorized'}, default=str)}\n\n",),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        return response

    # Subscribe to user events
    pubsub = subscribe_to_user_events(user.id)

    if not pubsub:
        response = StreamingHttpResponse(
            (f"event: error\ndata: {json.dumps({'error': 'Redis not available'}, default=str)}\n\n",),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        return response

    # Get college ID if available
    college_id = getattr(user, 'college_id', None)

    # Also subscribe to college events if college_id exists
    if college_id:
        college_pubsub = subscribe_to_college_events(college_id)
        # Note: For simplicity, we're only using user pubsub here
        # In production, you might want to merge both streams

    # Create streaming response
    response = StreamingHttpResponse(
        event_stream_generator(pubsub, user.id, college_id),
        content_type='text/event-stream'
    )

    # SSE headers
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
    response['Connection'] = 'keep-alive'

    logger.info(f"SSE connection established for user {user.id}")

    return response


@require_http_methods(["GET"])
def sse_test(request):
    """
    Test SSE endpoint to verify SSE is working.

    URL: /api/v1/communication/sse/test/

    Returns:
        StreamingHttpResponse: Test SSE stream
    """
    def test_generator():
        for i in range(5):
            yield f"event: test\n"
            yield f"data: {json.dumps({'count': i, 'message': f'Test event {i}'}, default=str)}\n\n"
            time.sleep(1)

        yield f"event: complete\n"
        yield f"data: {json.dumps({'message': 'Test complete'}, default=str)}\n\n"

    response = StreamingHttpResponse(
        test_generator(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'

    return response
