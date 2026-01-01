"""
Serializers for approval and notification models.
"""
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from .models import ApprovalRequest, ApprovalAction, Notification

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for approvals and notifications."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ApprovalActionSerializer(serializers.ModelSerializer):
    """Serializer for approval actions."""
    actor_details = UserBasicSerializer(source='actor', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ApprovalAction
        fields = [
            'id', 'approval_request', 'actor', 'actor_details',
            'action', 'action_display', 'comment', 'actioned_at',
            'ip_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'actioned_at', 'created_at', 'updated_at']


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """Serializer for approval requests."""
    requester_details = UserBasicSerializer(source='requester', read_only=True)
    approvers_details = UserBasicSerializer(source='approvers', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    actions = ApprovalActionSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'college', 'requester', 'requester_details',
            'request_type', 'request_type_display', 'title', 'description',
            'priority', 'priority_display', 'content_type', 'object_id',
            'status', 'status_display', 'approvers', 'approvers_details',
            'requires_approval_count', 'current_approval_count',
            'submitted_at', 'reviewed_at', 'deadline', 'metadata',
            'attachment', 'actions', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_approval_count', 'submitted_at', 'reviewed_at',
            'created_at', 'updated_at'
        ]


class ApprovalRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating approval requests (simplified)."""

    class Meta:
        model = ApprovalRequest
        fields = [
            'college', 'requester', 'request_type', 'title', 'description',
            'priority', 'content_type', 'object_id', 'approvers',
            'requires_approval_count', 'deadline', 'metadata', 'attachment'
        ]

    def create(self, validated_data):
        approvers = validated_data.pop('approvers', [])
        instance = ApprovalRequest.objects.create(**validated_data)
        if approvers:
            instance.approvers.set(approvers)
        return instance


class FeePaymentApprovalRequestSerializer(serializers.Serializer):
    """Specialized serializer for fee payment approval requests."""
    fee_collection_id = serializers.IntegerField(required=True)
    title = serializers.CharField(max_length=300, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high', 'urgent'],
        default='medium'
    )
    approver_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1,
        help_text="List of user IDs who can approve this request"
    )
    deadline_hours = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=720,  # 30 days max
        help_text="Deadline in hours from now"
    )
    attachment = serializers.FileField(required=False, allow_null=True)


class ApprovalActionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating approval actions."""

    class Meta:
        model = ApprovalAction
        fields = ['approval_request', 'actor', 'action', 'comment', 'ip_address']


class ApproveRejectSerializer(serializers.Serializer):
    """Serializer for approve/reject actions."""
    action = serializers.ChoiceField(choices=['approve', 'reject'], required=True)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=1000)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display',
            'content_type', 'object_id', 'action_url',
            'is_read', 'read_at', 'is_sent', 'sent_at',
            'expires_at', 'metadata', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_sent', 'sent_at', 'created_at', 'updated_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""

    class Meta:
        model = Notification
        fields = [
            'recipient', 'notification_type', 'title', 'message',
            'priority', 'content_type', 'object_id', 'action_url',
            'expires_at', 'metadata'
        ]


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for creating bulk notifications."""
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1,
        help_text="List of user IDs to notify"
    )
    notification_type = serializers.ChoiceField(
        choices=Notification.NOTIFICATION_TYPES,
        required=True
    )
    title = serializers.CharField(max_length=300, required=True)
    message = serializers.CharField(required=True, style={'base_template': 'textarea.html'})
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        default='medium'
    )
    action_url = serializers.CharField(max_length=500, required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of notification IDs to mark as read (leave empty to mark all as read)"
    )
