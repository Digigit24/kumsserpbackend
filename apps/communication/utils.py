from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone


def send_notification(user_id, title, message, notification_type='info', extra_data=None, notification_id=None):
    """
    Utility to send real-time notifications to a specific user via WebSockets.
    """
    channel_layer = get_channel_layer()
    payload = {
        "type": "notify",
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

    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        payload
    )


def broadcast_college_notification(college_id, title, message, notification_type='info', notification_id=None):
    """
    Utility to send real-time notifications to all users in a college.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"college_notifications_{college_id}",
        {
            "type": "notify",
            "id": notification_id,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "timestamp": timezone.now().isoformat(),
        }
    )
