"""
WebSocket Microservice Integration
Provides Django views to interact with the Node.js WebSocket microservice
"""

import requests
import logging
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

# WebSocket service URL
WEBSOCKET_SERVICE_URL = getattr(
    settings, 'WEBSOCKET_SERVICE_URL', 'http://localhost:3001'
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification_to_user(request):
    """
    Send a notification to a specific user via WebSocket microservice.

    POST /api/v1/communication/ws/notify/

    Body:
    {
        "recipient_id": "user-uuid",
        "type": "general",
        "title": "Notification Title",
        "message": "Notification message",
        "metadata": {}
    }
    """
    try:
        recipient_id = request.data.get('recipient_id')
        notification_type = request.data.get('type', 'general')
        title = request.data.get('title')
        message = request.data.get('message')
        metadata = request.data.get('metadata', {})

        if not recipient_id or not title or not message:
            return Response(
                {'error': 'recipient_id, title, and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Forward to WebSocket microservice
        response = requests.post(
            f'{WEBSOCKET_SERVICE_URL}/api/notify',
            json={
                'recipientId': str(recipient_id),
                'type': notification_type,
                'title': title,
                'message': message,
                'metadata': metadata,
            },
            timeout=5
        )

        if response.status_code == 200:
            return Response(response.json())
        else:
            logger.error(f'WebSocket service error: {response.text}')
            return Response(
                {'error': 'Failed to send notification'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.exceptions.RequestException as e:
        logger.error(f'Error connecting to WebSocket service: {e}')
        return Response(
            {'error': 'WebSocket service unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f'Error sending notification: {e}')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def broadcast_notification_to_college(request):
    """
    Broadcast a notification to all users in a college via WebSocket microservice.

    POST /api/v1/communication/ws/broadcast/

    Body:
    {
        "college_id": "college-uuid",
        "type": "general",
        "title": "Notification Title",
        "message": "Notification message",
        "metadata": {}
    }
    """
    try:
        college_id = request.data.get('college_id')
        notification_type = request.data.get('type', 'general')
        title = request.data.get('title')
        message = request.data.get('message')
        metadata = request.data.get('metadata', {})

        if not college_id or not title or not message:
            return Response(
                {'error': 'college_id, title, and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Forward to WebSocket microservice
        response = requests.post(
            f'{WEBSOCKET_SERVICE_URL}/api/broadcast',
            json={
                'collegeId': str(college_id),
                'type': notification_type,
                'title': title,
                'message': message,
                'metadata': metadata,
            },
            timeout=5
        )

        if response.status_code == 200:
            return Response(response.json())
        else:
            logger.error(f'WebSocket service error: {response.text}')
            return Response(
                {'error': 'Failed to broadcast notification'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.exceptions.RequestException as e:
        logger.error(f'Error connecting to WebSocket service: {e}')
        return Response(
            {'error': 'WebSocket service unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f'Error broadcasting notification: {e}')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_online_users(request):
    """
    Get list of currently online users from WebSocket microservice.

    GET /api/v1/communication/ws/online-users/
    """
    try:
        response = requests.get(
            f'{WEBSOCKET_SERVICE_URL}/api/online-users',
            timeout=5
        )

        if response.status_code == 200:
            return Response(response.json())
        else:
            logger.error(f'WebSocket service error: {response.text}')
            return Response(
                {'error': 'Failed to get online users'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except requests.exceptions.RequestException as e:
        logger.error(f'Error connecting to WebSocket service: {e}')
        return Response(
            {'error': 'WebSocket service unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        logger.error(f'Error getting online users: {e}')
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Helper function to send notification programmatically
def send_realtime_notification(recipient_id, notification_type, title, message, metadata=None):
    """
    Helper function to send real-time notification from Django code.

    Usage:
        from apps.communication.websocket_integration import send_realtime_notification

        send_realtime_notification(
            recipient_id=user.id,
            notification_type='approval_request',
            title='New Approval Request',
            message='You have a new approval request',
            metadata={'approval_id': approval.id}
        )
    """
    try:
        response = requests.post(
            f'{WEBSOCKET_SERVICE_URL}/api/notify',
            json={
                'recipientId': str(recipient_id),
                'type': notification_type,
                'title': title,
                'message': message,
                'metadata': metadata or {},
            },
            timeout=5
        )

        if response.status_code == 200:
            logger.info(f'Notification sent to user {recipient_id}')
            return True
        else:
            logger.error(f'Failed to send notification: {response.text}')
            return False

    except Exception as e:
        logger.error(f'Error sending notification: {e}')
        return False


# Helper function to broadcast notification programmatically
def broadcast_realtime_notification(college_id, notification_type, title, message, metadata=None):
    """
    Helper function to broadcast real-time notification from Django code.

    Usage:
        from apps.communication.websocket_integration import broadcast_realtime_notification

        broadcast_realtime_notification(
            college_id=college.id,
            notification_type='notice',
            title='New Notice Published',
            message='A new notice has been published',
            metadata={'notice_id': notice.id}
        )
    """
    try:
        response = requests.post(
            f'{WEBSOCKET_SERVICE_URL}/api/broadcast',
            json={
                'collegeId': str(college_id),
                'type': notification_type,
                'title': title,
                'message': message,
                'metadata': metadata or {},
            },
            timeout=5
        )

        if response.status_code == 200:
            logger.info(f'Notification broadcasted to college {college_id}')
            return True
        else:
            logger.error(f'Failed to broadcast notification: {response.text}')
            return False

    except Exception as e:
        logger.error(f'Error broadcasting notification: {e}')
        return False
