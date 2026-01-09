from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions.drf_permissions import ResourcePermission
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Max, F, Case, When, IntegerField
from django.utils import timezone
from datetime import timedelta

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
    Conversation,
    TypingIndicator,
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
from .redis_pubsub import (
    publish_message_event,
    publish_typing_event,
    publish_read_receipt,
    is_user_online,
    get_online_users,
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
    permission_classes = [ResourcePermission]
    resource_name = 'communication'
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
    permission_classes = [ResourcePermission]
    resource_name = 'communication'
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
    permission_classes = [ResourcePermission]
    resource_name = 'communication'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['message_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class BulkMessageViewSet(CollegeScopedModelViewSet):
    queryset = BulkMessage.objects.all_colleges().select_related('template', 'college')
    serializer_class = BulkMessageSerializer
    permission_classes = [ResourcePermission]
    resource_name = 'communication'
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
    queryset = ChatMessage.objects.select_related('sender', 'receiver', 'conversation')
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
        queryset = queryset.filter(Q(sender=user) | Q(receiver=user))

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Send a new message.

        Expected payload:
        {
            "receiver_id": 123,
            "message": "Hello!",
            "attachment": <file> (optional)
        }
        """
        receiver_id = request.data.get('receiver_id')
        message_content = request.data.get('message', '').strip()
        attachment = request.data.get('attachment')

        if not receiver_id:
            return Response(
                {'error': 'receiver_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not message_content and not attachment:
            return Response(
                {'error': 'message or attachment is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create receiver
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Receiver not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create conversation
        conversation = Conversation.get_or_create_conversation(request.user, receiver)

        # Create message
        message = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            conversation=conversation,
            message=message_content,
            attachment=attachment
        )

        # Update conversation metadata
        conversation.last_message = message_content[:100] if message_content else "[Attachment]"
        conversation.last_message_at = message.timestamp
        conversation.last_message_by = request.user
        conversation.increment_unread(receiver)
        conversation.save()

        # Publish real-time event via Redis
        attachment_url = None
        if message.attachment:
            try:
                attachment_url = message.attachment.url
            except:
                attachment_url = str(message.attachment)

        message_data = {
            'id': message.id,
            'sender_id': request.user.id,
            'sender_name': request.user.get_full_name() or request.user.username,
            'receiver_id': receiver.id,
            'message': message_content,
            'attachment': attachment_url,
            'attachment_type': message.attachment_type,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read,
            'conversation_id': conversation.id,
        }
        publish_message_event(receiver.id, message_data)

        # Serialize and return
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='conversations')
    def conversations(self, request):
        """
        Get list of all conversations for the current user.

        Returns conversations with:
        - Other user's info
        - Last message preview
        - Unread count
        - Online status
        - Last message timestamp

        Ordered by most recent first.
        """
        user = request.user

        # Get all conversations where user is participant
        conversations_as_user1 = Conversation.objects.filter(
            user1=user, is_active=True
        ).select_related('user2', 'last_message_by')

        conversations_as_user2 = Conversation.objects.filter(
            user2=user, is_active=True
        ).select_related('user1', 'last_message_by')

        # Combine and format
        conversations_data = []

        for conv in conversations_as_user1:
            other_user = conv.user2
            conversations_data.append({
                'conversation_id': conv.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'full_name': other_user.get_full_name() or other_user.username,
                    'avatar': other_user.avatar.url if other_user.avatar else None,
                    'is_online': is_user_online(other_user.id),
                },
                'last_message': conv.last_message,
                'last_message_at': conv.last_message_at,
                'last_message_by_me': conv.last_message_by_id == user.id if conv.last_message_by else False,
                'unread_count': conv.unread_count_user1,
                'updated_at': conv.updated_at,
            })

        for conv in conversations_as_user2:
            other_user = conv.user1
            conversations_data.append({
                'conversation_id': conv.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'full_name': other_user.get_full_name() or other_user.username,
                    'avatar': other_user.avatar.url if other_user.avatar else None,
                    'is_online': is_user_online(other_user.id),
                },
                'last_message': conv.last_message,
                'last_message_at': conv.last_message_at,
                'last_message_by_me': conv.last_message_by_id == user.id if conv.last_message_by else False,
                'unread_count': conv.unread_count_user2,
                'updated_at': conv.updated_at,
            })

        # Sort by last message timestamp
        conversations_data.sort(key=lambda x: x['last_message_at'] or timezone.now(), reverse=True)

        return Response(conversations_data)

    @action(detail=False, methods=['get'], url_path='conversation/(?P<other_user_id>[^/.]+)')
    def conversation_messages(self, request, other_user_id=None):
        """
        Get all messages in a conversation with a specific user.

        URL: /api/v1/communication/chats/conversation/{other_user_id}/

        Query params:
        - limit: Number of messages to return (default: 50)
        - offset: Offset for pagination (default: 0)
        - before_id: Get messages before this message ID (for infinite scroll)
        """
        user = request.user

        # Get other user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create conversation
        conversation = Conversation.get_or_create_conversation(user, other_user)

        # Get messages
        messages = ChatMessage.objects.filter(
            conversation=conversation,
            is_active=True
        ).select_related('sender', 'receiver').order_by('-timestamp')

        # Handle pagination
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        before_id = request.query_params.get('before_id')

        if before_id:
            messages = messages.filter(id__lt=before_id)

        messages = messages[offset:offset + limit]

        # Serialize messages
        serializer = self.get_serializer(messages, many=True)

        # Also return conversation metadata
        return Response({
            'conversation_id': conversation.id,
            'messages': serializer.data,
            'other_user': {
                'id': other_user.id,
                'username': other_user.username,
                'full_name': other_user.get_full_name() or other_user.username,
                'avatar': other_user.avatar.url if other_user.avatar else None,
                'is_online': is_user_online(other_user.id),
            },
            'has_more': messages.count() == limit,
        })

    @action(detail=False, methods=['post'], url_path='mark-read')
    def mark_read(self, request):
        """
        Mark messages as read.

        Expected payload:
        {
            "message_ids": [1, 2, 3],  // Optional: specific message IDs
            "conversation_id": 123,     // Optional: mark all messages in conversation as read
            "sender_id": 456            // Optional: mark all messages from sender as read
        }
        """
        message_ids = request.data.get('message_ids', [])
        conversation_id = request.data.get('conversation_id')
        sender_id = request.data.get('sender_id')

        user = request.user
        messages_to_mark = ChatMessage.objects.filter(receiver=user, is_read=False)

        if message_ids:
            messages_to_mark = messages_to_mark.filter(id__in=message_ids)
        elif conversation_id:
            messages_to_mark = messages_to_mark.filter(conversation_id=conversation_id)
        elif sender_id:
            messages_to_mark = messages_to_mark.filter(sender_id=sender_id)
        else:
            return Response(
                {'error': 'Provide message_ids, conversation_id, or sender_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark as read
        read_time = timezone.now()
        count = messages_to_mark.update(is_read=True, read_at=read_time)

        # Update conversation unread count
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                conversation.reset_unread(user)
            except Conversation.DoesNotExist:
                pass

        # Publish read receipts
        for msg in messages_to_mark:
            publish_read_receipt(
                msg.sender_id,
                msg.id,
                user.id,
                user.get_full_name() or user.username
            )

        return Response({
            'success': True,
            'marked_count': count,
            'read_at': read_time.isoformat()
        })

    @action(detail=False, methods=['post'], url_path='typing')
    def typing_indicator(self, request):
        """
        Send typing indicator.

        Expected payload:
        {
            "receiver_id": 123,
            "is_typing": true
        }
        """
        receiver_id = request.data.get('receiver_id')
        is_typing = request.data.get('is_typing', True)

        if not receiver_id:
            return Response(
                {'error': 'receiver_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get receiver
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Receiver not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update or create typing indicator
        TypingIndicator.objects.update_or_create(
            user=request.user,
            conversation_partner=receiver,
            defaults={'is_typing': is_typing}
        )

        # Publish typing event
        publish_typing_event(
            receiver.id,
            request.user.id,
            request.user.get_full_name() or request.user.username,
            is_typing
        )

        return Response({'success': True})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """
        Get total unread message count for the current user.

        Returns:
        {
            "total_unread": 42,
            "conversations": [
                {"conversation_id": 1, "unread_count": 5, "other_user_id": 123},
                ...
            ]
        }
        """
        user = request.user

        # Get all conversations with unread messages
        conversations_as_user1 = Conversation.objects.filter(
            user1=user,
            unread_count_user1__gt=0,
            is_active=True
        ).select_related('user2')

        conversations_as_user2 = Conversation.objects.filter(
            user2=user,
            unread_count_user2__gt=0,
            is_active=True
        ).select_related('user1')

        conversations_data = []
        total_unread = 0

        for conv in conversations_as_user1:
            unread = conv.unread_count_user1
            total_unread += unread
            conversations_data.append({
                'conversation_id': conv.id,
                'unread_count': unread,
                'other_user_id': conv.user2.id,
                'other_user_name': conv.user2.get_full_name() or conv.user2.username,
            })

        for conv in conversations_as_user2:
            unread = conv.unread_count_user2
            total_unread += unread
            conversations_data.append({
                'conversation_id': conv.id,
                'unread_count': unread,
                'other_user_id': conv.user1.id,
                'other_user_name': conv.user1.get_full_name() or conv.user1.username,
            })

        return Response({
            'total_unread': total_unread,
            'conversations': conversations_data
        })

    @action(detail=False, methods=['get'], url_path='online-users')
    def online_users(self, request):
        """
        Get list of currently online user IDs.

        Returns:
        {
            "online_users": [123, 456, 789]
        }
        """
        online_user_ids = list(get_online_users())
        return Response({'online_users': online_user_ids})
