# -*- coding: utf-8 -*-
"""
Approval models for managing approval workflows across the system.
Handles fee payment approvals, document approvals, and other approval processes.
"""
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.core.models import AuditModel, College


class ApprovalRequest(AuditModel):
    """
    Generic approval request model that can be used for any approval workflow.
    Uses generic foreign key to link to any model (FeeCollection, Document, etc.)
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    REQUEST_TYPES = [
        ('fee_payment', 'Fee Payment'),
        ('document_verification', 'Document Verification'),
        ('leave_request', 'Leave Request'),
        ('expense_claim', 'Expense Claim'),
        ('other', 'Other'),
    ]

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='approval_requests',
        help_text="College reference"
    )

    # Requester information
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approval_requests_made',
        help_text="User who made the request"
    )

    # Request details
    request_type = models.CharField(
        max_length=50,
        choices=REQUEST_TYPES,
        help_text="Type of approval request"
    )
    title = models.CharField(max_length=300, help_text="Request title")
    description = models.TextField(blank=True, help_text="Request description")
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Request priority"
    )

    # Generic relation to any model (FeeCollection, Document, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Content type of the related object"
    )
    object_id = models.PositiveIntegerField(help_text="ID of the related object")
    related_object = GenericForeignKey('content_type', 'object_id')

    # Approval status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Approval status"
    )

    # Approvers (can have multiple approvers for multi-level approval)
    approvers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='approval_requests_to_review',
        help_text="Users who can approve this request"
    )

    # Approval workflow
    requires_approval_count = models.IntegerField(
        default=1,
        help_text="Number of approvals required (for multi-level approval)"
    )
    current_approval_count = models.IntegerField(
        default=0,
        help_text="Current number of approvals received"
    )

    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True, help_text="Submission time")
    reviewed_at = models.DateTimeField(null=True, blank=True, help_text="Review time")
    deadline = models.DateTimeField(null=True, blank=True, help_text="Approval deadline")

    # Additional data (JSON for flexibility)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for the request"
    )

    # Attachments
    attachment = models.FileField(
        upload_to='approval_attachments/',
        null=True,
        blank=True,
        help_text="Supporting document/attachment"
    )

    class Meta:
        db_table = 'approval_request'
        verbose_name = 'Approval Request'
        verbose_name_plural = 'Approval Requests'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['college', 'status', 'request_type']),
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['submitted_at', 'deadline']),
        ]

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.title} ({self.status})"

    def approve(self, approver):
        """Mark request as approved by an approver."""
        self.current_approval_count += 1
        if self.current_approval_count >= self.requires_approval_count:
            self.status = 'approved'
            self.reviewed_at = timezone.now()
        self.save()

    def reject(self, approver, reason):
        """Mark request as rejected by an approver."""
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.metadata['rejection_reason'] = reason
        self.save()

    def cancel(self):
        """Cancel the approval request."""
        self.status = 'cancelled'
        self.reviewed_at = timezone.now()
        self.save()

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    @property
    def is_overdue(self):
        if self.deadline and self.status == 'pending':
            return timezone.now() > self.deadline
        return False


class ApprovalAction(AuditModel):
    """
    Tracks individual approval/rejection actions on approval requests.
    Provides audit trail for approval workflow.
    """

    ACTION_CHOICES = [
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('comment', 'Commented'),
        ('request_changes', 'Requested Changes'),
    ]

    approval_request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name='actions',
        help_text="Approval request"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approval_actions',
        help_text="User who performed the action"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Action taken"
    )

    comment = models.TextField(blank=True, help_text="Comment/reason for action")

    actioned_at = models.DateTimeField(auto_now_add=True, help_text="Action timestamp")

    # IP address tracking for security
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the actor"
    )

    class Meta:
        db_table = 'approval_action'
        verbose_name = 'Approval Action'
        verbose_name_plural = 'Approval Actions'
        ordering = ['-actioned_at']
        indexes = [
            models.Index(fields=['approval_request', 'action']),
            models.Index(fields=['actor', 'actioned_at']),
        ]

    def __str__(self):
        return f"{self.actor} {self.get_action_display()} - {self.approval_request}"


class Notification(AuditModel):
    """
    In-app notification model for notifying users about various events.
    Used for approval requests, status updates, etc.
    """

    NOTIFICATION_TYPES = [
        ('approval_request', 'Approval Request'),
        ('approval_approved', 'Approval Approved'),
        ('approval_rejected', 'Approval Rejected'),
        ('payment_received', 'Payment Received'),
        ('document_uploaded', 'Document Uploaded'),
        ('general', 'General Notification'),
        ('system', 'System Notification'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="Notification recipient"
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        help_text="Type of notification"
    )

    title = models.CharField(max_length=300, help_text="Notification title")
    message = models.TextField(help_text="Notification message")

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Notification priority"
    )

    # Link to related object (optional)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Content type of the related object"
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID of the related object")
    related_object = GenericForeignKey('content_type', 'object_id')

    # Action URL (where to redirect when clicked)
    action_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL to redirect to when notification is clicked"
    )

    # Read status
    is_read = models.BooleanField(default=False, help_text="Read status")
    read_at = models.DateTimeField(null=True, blank=True, help_text="Read timestamp")

    # Send status
    is_sent = models.BooleanField(default=False, help_text="Send status")
    sent_at = models.DateTimeField(auto_now_add=True, help_text="Sent timestamp")

    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Expiry time")

    # Additional data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata"
    )

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'sent_at']),
            models.Index(fields=['notification_type', 'sent_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.title} -> {self.recipient}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])

    @property
    def is_expired(self):
        """Check if notification has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
