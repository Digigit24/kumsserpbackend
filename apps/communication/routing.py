"""
WebSocket URL routing configuration.
Defines WebSocket endpoints for chat and notifications.
"""
from django.urls import re_path, path
from . import consumers

# WebSocket URL patterns
websocket_urlpatterns = [
    # Chat WebSocket endpoint
    # ws://domain/ws/chat/?token=YOUR_TOKEN
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),

    # Notifications WebSocket endpoint
    # ws://domain/ws/notifications/?token=YOUR_TOKEN
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
