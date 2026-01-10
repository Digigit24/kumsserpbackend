"""
Long polling views for real-time communication.
Replaces SSE with long polling approach using RabbitMQ.
"""
import json
import logging
import time
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .rabbitmq_queue import (
    get_rabbitmq,
    set_user_online,
    set_user_offline,
    get_queued_events,
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


# Helper functions removed - now using rabbitmq_queue.get_queued_events()


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

    rabbitmq_client = get_rabbitmq()
    if not rabbitmq_client.is_connected():
        return JsonResponse({
            'error': 'RabbitMQ not available',
            'message': 'RabbitMQ is not running or not accessible',
            'events': [],
            'setup_instructions': {
                'quick_start': 'See RABBITMQ_SETUP.md for installation guide',
                'docker': 'docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management',
                'windows': 'Download from https://www.rabbitmq.com/install-windows.html',
                'linux': 'sudo apt-get install rabbitmq-server && sudo systemctl start rabbitmq-server',
                'test': 'python manage.py check_rabbitmq',
                'troubleshooting': 'Check if RabbitMQ service is running'
            },
            'common_issues': [
                'RabbitMQ not installed - Install from rabbitmq.com',
                'RabbitMQ service not running - Start the service',
                'Port 5672 blocked - Check firewall settings',
                'Missing pika package - Run: pip install pika==1.3.2'
            ]
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
        events = get_queued_events(user.id, college_id)

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


@require_http_methods(["GET"])
def sse_migration_notice(request):
    """
    Migration notice for old SSE endpoint.
    Returns helpful error message directing to new polling endpoint.

    Old URL: /api/v1/communication/sse/events/
    New URL: /api/v1/communication/poll/events/
    """
    return JsonResponse({
        'error': 'SSE endpoint has been replaced',
        'message': 'Server-Sent Events have been replaced with Long Polling using RabbitMQ',
        'migration': {
            'old_endpoint': '/api/v1/communication/sse/events/',
            'new_endpoint': '/api/v1/communication/poll/events/',
            'method': 'GET',
            'authentication': 'Token in query parameter (?token=XXX) or Authorization header'
        },
        'breaking_changes': [
            'Replace EventSource with fetch() in a loop',
            'Use new endpoint: /api/v1/communication/poll/events/',
            'Events now returned as JSON array in "events" field',
            'Client must immediately poll again after receiving response'
        ],
        'documentation': '/apps/communication/LONG_POLLING_GUIDE.md',
        'test_endpoint': '/api/v1/communication/poll/test/'
    }, status=410)  # 410 Gone - resource permanently removed
