"""
URL configuration for Communication app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    NoticeViewSet,
    NoticeVisibilityViewSet,
    EventViewSet,
    EventRegistrationViewSet,
    MessageTemplateViewSet,
    BulkMessageViewSet,
    MessageLogViewSet,
    NotificationRuleViewSet,
    ChatMessageViewSet,
)
from .long_polling_views import long_poll_events, poll_test, disconnect

router = DefaultRouter()
router.register(r'notices', NoticeViewSet, basename='notice')
router.register(r'notice-visibility', NoticeVisibilityViewSet, basename='noticevisibility')
router.register(r'events', EventViewSet, basename='event')
router.register(r'event-registrations', EventRegistrationViewSet, basename='eventregistration')
router.register(r'message-templates', MessageTemplateViewSet, basename='messagetemplate')
router.register(r'bulk-messages', BulkMessageViewSet, basename='bulkmessage')
router.register(r'message-logs', MessageLogViewSet, basename='messagelog')
router.register(r'notification-rules', NotificationRuleViewSet, basename='notificationrule')
router.register(r'chats', ChatMessageViewSet, basename='chatmessage')

urlpatterns = [
    # Long Polling endpoints for real-time communication
    path('poll/events/', long_poll_events, name='long-poll-events'),
    path('poll/test/', poll_test, name='poll-test'),
    path('poll/disconnect/', disconnect, name='poll-disconnect'),

    # REST API endpoints
    path('', include(router.urls)),
]
