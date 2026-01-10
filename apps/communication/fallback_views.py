"""
Temporary fallback view for long polling when RabbitMQ is not available.
This allows development to continue while setting up RabbitMQ.
"""
import json
import logging
import time
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def get_user_from_token(request):
    """Authenticate user from token."""
    token_key = request.GET.get('token')

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
        return None


@require_http_methods(["GET"])
def poll_events_fallback(request):
    """
    Fallback long polling endpoint when RabbitMQ is not available.
    Returns empty events after timeout to allow frontend to continue working.

    This is a temporary solution for development.
    Install and start RabbitMQ for production use.
    """
    user = get_user_from_token(request)

    if not user or not user.is_authenticated:
        return JsonResponse({
            'error': 'Unauthorized',
            'events': []
        }, status=401)

    # Simulate polling timeout
    time.sleep(1)

    return JsonResponse({
        'events': [],
        'timestamp': time.time(),
        'warning': 'RabbitMQ not available - using fallback mode',
        'message': 'Real-time features disabled. Install RabbitMQ to enable.',
        'setup_instructions': {
            'windows': 'Download from https://www.rabbitmq.com/install-windows.html',
            'linux': 'sudo apt-get install rabbitmq-server',
            'docker': 'docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management',
            'test': 'python manage.py check_rabbitmq'
        }
    })
