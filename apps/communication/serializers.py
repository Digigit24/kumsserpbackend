from rest_framework import serializers

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


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class NoticeVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeVisibility
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = '__all__'


class MessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = '__all__'


class BulkMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkMessage
        fields = '__all__'


class MessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = '__all__'


class NotificationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRule
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.get_full_name', read_only=True)

    class Meta:
        model = ChatMessage
        fields = '__all__'
