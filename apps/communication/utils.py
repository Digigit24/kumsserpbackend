from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def send_notification(user_id, title, message, notification_type='info', extra_data=None):
    """
    Utility to send real-time notifications to a specific user via WebSockets.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user_id}",
        {
            "type": "notify",
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "extra_data": extra_data or {}
        }
    )

def broadcast_college_notification(college_id, title, message, notification_type='info'):
    """
    Utility to send real-time notifications to all users in a college.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"college_notifications_{college_id}",
        {
            "type": "notify",
            "title": title,
            "message": message,
            "notification_type": notification_type
        }
    )
