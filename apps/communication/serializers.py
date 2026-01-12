from rest_framework import serializers
from django.contrib.auth import get_user_model

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

User = get_user_model()


class NoticeSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Notice
        fields = '__all__'


class NoticeVisibilitySerializer(serializers.ModelSerializer):
    notice_title = serializers.CharField(source='notice.title', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = NoticeVisibility
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class EventRegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = EventRegistration
        fields = '__all__'


class MessageTemplateSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = MessageTemplate
        fields = '__all__'


class BulkMessageSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = BulkMessage
        fields = '__all__'


class MessageLogSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    bulk_message_title = serializers.CharField(source='bulk_message.title', read_only=True)

    class Meta:
        model = MessageLog
        fields = '__all__'


class NotificationRuleSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = NotificationRule
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    receiver_avatar = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'sender_name', 'sender_username', 'sender_avatar',
            'receiver', 'receiver_name', 'receiver_username', 'receiver_avatar',
            'conversation', 'message', 'attachment', 'attachment_url', 'attachment_type',
            'is_read', 'read_at', 'delivered_at', 'timestamp',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'sender', 'timestamp', 'created_at', 'updated_at']

    def get_sender_avatar(self, obj):
        if obj.sender and obj.sender.avatar:
            try:
                return obj.sender.avatar.url
            except:
                return None
        return None

    def get_receiver_avatar(self, obj):
        if obj.receiver and obj.receiver.avatar:
            try:
                return obj.receiver.avatar.url
            except:
                return None
        return None

    def get_attachment_url(self, obj):
        if obj.attachment:
            try:
                return obj.attachment.url
            except:
                return str(obj.attachment)
        return None


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for conversations."""
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'avatar_url']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_avatar_url(self, obj):
        if obj.avatar:
            try:
                return obj.avatar.url
            except:
                return None
        return None


class ConversationSerializer(serializers.ModelSerializer):
    user1_info = UserBasicSerializer(source='user1', read_only=True)
    user2_info = UserBasicSerializer(source='user2', read_only=True)
    last_message_by_info = UserBasicSerializer(source='last_message_by', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'user1', 'user1_info', 'user2', 'user2_info',
            'last_message', 'last_message_at', 'last_message_by', 'last_message_by_info',
            'unread_count_user1', 'unread_count_user2',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TypingIndicatorSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    conversation_partner_name = serializers.CharField(source='conversation_partner.get_full_name', read_only=True)

    class Meta:
        model = TypingIndicator
        fields = [
            'id', 'user', 'user_name', 'conversation_partner',
            'conversation_partner_name', 'is_typing', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
