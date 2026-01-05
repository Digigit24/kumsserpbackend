from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedMixin, CollegeScopedModelViewSet
from .models import (
    Notice,
    NoticeVisibility,
    Event,
    EventRegistration,
    MessageTemplate,
    BulkMessage,
    MessageLog,
    NotificationRule,
    ChatMessage,
)
from .serializers import (
    NoticeSerializer,
    NoticeVisibilitySerializer,
    EventSerializer,
    EventRegistrationSerializer,
    MessageTemplateSerializer,
    BulkMessageSerializer,
    MessageLogSerializer,
    NotificationRuleSerializer,
    ChatMessageSerializer,
)


class RelatedCollegeScopedModelViewSet(CollegeScopedMixin, viewsets.ModelViewSet):
    """
    Scopes by college via a related lookup path when model lacks direct college FK.
    """
    related_college_lookup = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        college_id = self.get_college_id(required=False)
        user = getattr(self.request, 'user', None)

        if college_id == 'all' or (user and (user.is_superuser or user.is_staff) and not college_id):
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        if not self.related_college_lookup:
            return queryset.none()

        return queryset.filter(**{self.related_college_lookup: college_id})


class NoticeViewSet(CollegeScopedModelViewSet):
    queryset = Notice.objects.all_colleges()
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['publish_date', 'is_published', 'is_urgent', 'is_active']
    search_fields = ['title', 'content']
    ordering_fields = ['publish_date', 'created_at']
    ordering = ['-publish_date']


class NoticeVisibilityViewSet(RelatedCollegeScopedModelViewSet):
    queryset = NoticeVisibility.objects.select_related('notice')
    serializer_class = NoticeVisibilitySerializer
    related_college_lookup = 'notice__college_id'
    filterset_fields = ['notice', 'target_type', 'class_obj', 'section', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class EventViewSet(CollegeScopedModelViewSet):
    queryset = Event.objects.all_colleges()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_date', 'registration_required', 'is_active']
    search_fields = ['title', 'description', 'organizer']
    ordering_fields = ['event_date', 'created_at']
    ordering = ['-event_date']


class EventRegistrationViewSet(RelatedCollegeScopedModelViewSet):
    queryset = EventRegistration.objects.select_related('event', 'user')
    serializer_class = EventRegistrationSerializer
    related_college_lookup = 'event__college_id'
    filterset_fields = ['event', 'user', 'status', 'is_active']
    ordering_fields = ['registration_date', 'created_at']
    ordering = ['-registration_date']


class MessageTemplateViewSet(CollegeScopedModelViewSet):
    queryset = MessageTemplate.objects.all_colleges()
    serializer_class = MessageTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['message_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class BulkMessageViewSet(CollegeScopedModelViewSet):
    queryset = BulkMessage.objects.all_colleges().select_related('template', 'college')
    serializer_class = BulkMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'message_type', 'scheduled_at', 'is_active']
    search_fields = ['title']
    ordering_fields = ['scheduled_at', 'sent_at', 'created_at']
    ordering = ['-created_at']


class MessageLogViewSet(RelatedCollegeScopedModelViewSet):
    queryset = MessageLog.objects.select_related('bulk_message', 'recipient')
    serializer_class = MessageLogSerializer
    related_college_lookup = 'bulk_message__college_id'
    filterset_fields = ['bulk_message', 'recipient', 'status', 'message_type', 'is_active']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-created_at']


class NotificationRuleViewSet(CollegeScopedModelViewSet):
    queryset = NotificationRule.objects.all_colleges().select_related('template', 'college')
    serializer_class = NotificationRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'is_enabled', 'is_active']
    search_fields = ['name', 'event_type']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.select_related('sender', 'receiver')
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sender', 'receiver', 'is_read', 'is_active']
    ordering_fields = ['timestamp', 'created_at']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter messages to show only those sent to or from the current user."""
        queryset = super().get_queryset()
        user = self.request.user

        # Only show messages where user is sender OR receiver
        from django.db.models import Q
        queryset = queryset.filter(Q(sender=user) | Q(receiver=user))

        return queryset
