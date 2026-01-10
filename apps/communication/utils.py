from django.utils import timezone
from .rabbitmq_queue import publish_notification, publish_college_notification


def send_notification(user_id, title, message, notification_type='info', extra_data=None, notification_id=None):
    """
    Utility to send real-time notifications to a specific user via RabbitMQ.
    """
    payload = {
        "id": notification_id,
        "title": title,
        "message": message,
        "notification_type": notification_type,
        "timestamp": timezone.now().isoformat(),
    }

    if extra_data:
        for key, value in extra_data.items():
            if key == 'type':
                continue
            payload[key] = value
        if payload.get('id') is None:
            payload['id'] = extra_data.get('id')
        if payload.get('timestamp') is None:
            payload['timestamp'] = extra_data.get('timestamp')

    publish_notification(user_id, payload)


def broadcast_college_notification(college_id, title, message, notification_type='info', notification_id=None):
    """
    Utility to send real-time notifications to all users in a college via RabbitMQ.
    """
    payload = {
        "id": notification_id,
        "title": title,
        "message": message,
        "notification_type": notification_type,
        "timestamp": timezone.now().isoformat(),
    }

    publish_college_notification(college_id, payload)
