"""
Communication models for notices, events, messaging, and notifications.
"""
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import CollegeScopedModel, AuditModel, College
from apps.accounts.models import User
from apps.academic.models import Class, Section


class Notice(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='notices',
        help_text="College reference"
    )
    title = models.CharField(max_length=300, help_text="Notice title")
    content = models.TextField(help_text="Notice content")
    publish_date = models.DateField(help_text="Publish date")
    expiry_date = models.DateField(null=True, blank=True, help_text="Expiry date")
    attachment = models.FileField(upload_to='notice_attachments/', null=True, blank=True, help_text="Attachment")
    is_urgent = models.BooleanField(default=False, help_text="Urgent flag")
    is_published = models.BooleanField(default=False, help_text="Published flag")

    class Meta:
        db_table = 'notice'
        indexes = [
            models.Index(fields=['college', 'publish_date', 'is_published']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.expiry_date and self.expiry_date < self.publish_date:
            raise ValidationError("Expiry date cannot be before publish date.")


class NoticeVisibility(AuditModel):
    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name='visibilities',
        help_text="Notice"
    )
    target_type = models.CharField(max_length=20, help_text="Type (all/class/section)")
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notice_visibilities',
        help_text="Class"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notice_visibilities',
        help_text="Section"
    )

    class Meta:
        db_table = 'notice_visibility'
        indexes = [
            models.Index(fields=['notice', 'class_obj', 'section']),
        ]

    def __str__(self):
        return f"Visibility for {self.notice}"

    def clean(self):
        if self.target_type == 'class' and not self.class_obj:
            raise ValidationError("Class is required when target_type is 'class'.")
        if self.target_type == 'section' and not self.section:
            raise ValidationError("Section is required when target_type is 'section'.")


class Event(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='events',
        help_text="College reference"
    )
    title = models.CharField(max_length=300, help_text="Event title")
    description = models.TextField(help_text="Description")
    event_date = models.DateField(help_text="Event date")
    start_time = models.TimeField(help_text="Start time")
    end_time = models.TimeField(help_text="End time")
    venue = models.CharField(max_length=200, null=True, blank=True, help_text="Venue")
    organizer = models.CharField(max_length=200, null=True, blank=True, help_text="Organizer")
    max_participants = models.IntegerField(null=True, blank=True, help_text="Max participants")
    registration_required = models.BooleanField(default=False, help_text="Registration required")
    registration_deadline = models.DateField(null=True, blank=True, help_text="Registration deadline")
    image = models.ImageField(upload_to='event_images/', null=True, blank=True, help_text="Event image")

    class Meta:
        db_table = 'event'
        indexes = [
            models.Index(fields=['college', 'event_date']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")


class EventRegistration(AuditModel):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        help_text="Event"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        help_text="User"
    )
    registration_date = models.DateField(help_text="Registration date")
    status = models.CharField(max_length=20, default='registered', help_text="Status")

    class Meta:
        db_table = 'event_registration'
        unique_together = ['event', 'user']
        indexes = [
            models.Index(fields=['event', 'user']),
        ]

    def __str__(self):
        return f"{self.user} -> {self.event}"


class MessageTemplate(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='message_templates',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Template name")
    code = models.CharField(max_length=50, help_text="Template code")
    message_type = models.CharField(max_length=20, help_text="Type (SMS/Email/WhatsApp)")
    content = models.TextField(help_text="Template content")
    variables = models.CharField(max_length=500, null=True, blank=True, help_text="Variables (comma-separated)")

    class Meta:
        db_table = 'message_template'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class BulkMessage(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='bulk_messages',
        help_text="College reference"
    )
    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bulk_messages',
        help_text="Template"
    )
    title = models.CharField(max_length=200, help_text="Message title")
    message_type = models.CharField(max_length=20, help_text="Type (SMS/Email/WhatsApp)")
    recipient_type = models.CharField(max_length=20, help_text="Recipients type")
    total_recipients = models.IntegerField(default=0, help_text="Total recipients")
    sent_count = models.IntegerField(default=0, help_text="Sent count")
    failed_count = models.IntegerField(default=0, help_text="Failed count")
    status = models.CharField(max_length=20, default='pending', help_text="Status")
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text="Scheduled time")
    sent_at = models.DateTimeField(null=True, blank=True, help_text="Sent time")

    class Meta:
        db_table = 'bulk_message'
        indexes = [
            models.Index(fields=['college', 'status', 'scheduled_at']),
        ]

    def __str__(self):
        return self.title


class MessageLog(AuditModel):
    bulk_message = models.ForeignKey(
        BulkMessage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='logs',
        help_text="Bulk message"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_logs',
        help_text="Recipient"
    )
    message_type = models.CharField(max_length=20, help_text="Type (SMS/Email/WhatsApp)")
    phone_email = models.CharField(max_length=200, help_text="Phone/Email")
    message = models.TextField(help_text="Message content")
    status = models.CharField(max_length=20, default='pending', help_text="Status")
    sent_at = models.DateTimeField(null=True, blank=True, help_text="Sent time")
    delivered_at = models.DateTimeField(null=True, blank=True, help_text="Delivered time")
    error_message = models.TextField(null=True, blank=True, help_text="Error message")

    class Meta:
        db_table = 'message_log'
        indexes = [
            models.Index(fields=['bulk_message', 'recipient', 'status']),
        ]

    def __str__(self):
        return f"Message to {self.recipient}"


class NotificationRule(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='notification_rules',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Rule name")
    event_type = models.CharField(max_length=50, help_text="Event type")
    channels = models.CharField(max_length=100, help_text="Channels (SMS,Email,WhatsApp)")
    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notification_rules',
        help_text="Template"
    )
    is_enabled = models.BooleanField(default=True, help_text="Enabled flag")

    class Meta:
        db_table = 'notification_rule'
        indexes = [
            models.Index(fields=['college', 'event_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.event_type})"


class Conversation(AuditModel):
    """
    Represents a conversation between two users.
    Stores metadata about the conversation for quick access.
    """
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_as_user1',
        help_text="First user in conversation"
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_as_user2',
        help_text="Second user in conversation"
    )
    last_message = models.TextField(null=True, blank=True, help_text="Last message preview")
    last_message_at = models.DateTimeField(null=True, blank=True, help_text="Last message timestamp")
    last_message_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_messages',
        help_text="User who sent last message"
    )
    unread_count_user1 = models.IntegerField(default=0, help_text="Unread count for user1")
    unread_count_user2 = models.IntegerField(default=0, help_text="Unread count for user2")

    class Meta:
        db_table = 'conversation'
        unique_together = ['user1', 'user2']
        indexes = [
            models.Index(fields=['user1', 'user2']),
            models.Index(fields=['last_message_at']),
        ]

    def __str__(self):
        return f"Conversation: {self.user1.username} <-> {self.user2.username}"

    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        """Get or create a conversation between two users, ensuring consistent ordering."""
        if user1.id > user2.id:
            user1, user2 = user2, user1

        conversation, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2
        )
        return conversation

    def get_other_user(self, user):
        """Get the other user in the conversation."""
        return self.user2 if user.id == self.user1.id else self.user1

    def get_unread_count(self, user):
        """Get unread count for a specific user."""
        if user.id == self.user1.id:
            return self.unread_count_user1
        return self.unread_count_user2

    def increment_unread(self, for_user):
        """Increment unread count for a specific user."""
        if for_user.id == self.user1.id:
            self.unread_count_user1 += 1
        else:
            self.unread_count_user2 += 1
        self.save(update_fields=['unread_count_user1' if for_user.id == self.user1.id else 'unread_count_user2', 'updated_at'])

    def reset_unread(self, for_user):
        """Reset unread count for a specific user."""
        if for_user.id == self.user1.id:
            self.unread_count_user1 = 0
        else:
            self.unread_count_user2 = 0
        self.save(update_fields=['unread_count_user1' if for_user.id == self.user1.id else 'unread_count_user2', 'updated_at'])


class ChatMessage(AuditModel):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="Sender"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        help_text="Receiver"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True,
        help_text="Related conversation"
    )
    message = models.TextField(help_text="Message content", blank=True, default="")
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True, help_text="Attachment")
    attachment_type = models.CharField(max_length=20, null=True, blank=True, help_text="Attachment type (image/video/document)")
    is_read = models.BooleanField(default=False, help_text="Read flag")
    read_at = models.DateTimeField(null=True, blank=True, help_text="Read time")
    delivered_at = models.DateTimeField(null=True, blank=True, help_text="Delivered time")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp")

    class Meta:
        db_table = 'chat_message'
        indexes = [
            models.Index(fields=['sender', 'receiver', 'timestamp', 'is_read']),
            models.Index(fields=['conversation', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])

    def mark_delivered(self):
        if not self.delivered_at:
            self.delivered_at = datetime.now()
            self.save(update_fields=['delivered_at', 'updated_at'])


class TypingIndicator(models.Model):
    """
    Stores typing indicators for real-time display.
    Uses TTL (time to live) - records older than 5 seconds are considered stale.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='typing_indicators',
        help_text="User who is typing"
    )
    conversation_partner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='typing_to',
        help_text="User being typed to"
    )
    is_typing = models.BooleanField(default=True, help_text="Currently typing")
    timestamp = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    class Meta:
        db_table = 'typing_indicator'
        unique_together = ['user', 'conversation_partner']
        indexes = [
            models.Index(fields=['conversation_partner', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} typing to {self.conversation_partner.username}"
