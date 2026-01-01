"""
Admin configuration for approval and notification models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ApprovalRequest, ApprovalAction, Notification


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    """Admin interface for approval requests."""
    list_display = [
        'id', 'title', 'request_type', 'requester', 'status_badge',
        'priority', 'submitted_at', 'deadline', 'is_overdue_badge'
    ]
    list_filter = ['status', 'request_type', 'priority', 'submitted_at', 'college']
    search_fields = ['title', 'description', 'requester__username', 'requester__email']
    readonly_fields = [
        'submitted_at', 'reviewed_at', 'current_approval_count',
        'created_at', 'updated_at'
    ]
    filter_horizontal = ['approvers']
    date_hierarchy = 'submitted_at'

    fieldsets = (
        ('Request Information', {
            'fields': ('college', 'requester', 'request_type', 'title', 'description', 'priority')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id')
        }),
        ('Approval Workflow', {
            'fields': ('status', 'approvers', 'requires_approval_count', 'current_approval_count')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'reviewed_at', 'deadline')
        }),
        ('Additional Data', {
            'fields': ('metadata', 'attachment'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def is_overdue_badge(self, obj):
        """Display overdue status."""
        if obj.is_overdue:
<<<<<<< HEAD
            return format_html('<span style="color: red; font-weight: bold;"> OVERDUE</span>')
        return format_html('<span style="color: green;"> On Time</span>')
=======
            return format_html('<span style="color: red; font-weight: bold;">⚠ OVERDUE</span>')
        return format_html('<span style="color: green;">✓ On Time</span>')
>>>>>>> origin/claude/fix-approval-app-errors-Bwqp5
    is_overdue_badge.short_description = 'Deadline Status'


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    """Admin interface for approval actions."""
    list_display = [
        'id', 'approval_request', 'actor', 'action_badge',
        'actioned_at', 'ip_address'
    ]
    list_filter = ['action', 'actioned_at']
    search_fields = [
        'approval_request__title', 'actor__username',
        'actor__email', 'comment'
    ]
    readonly_fields = ['actioned_at', 'created_at', 'updated_at']
    date_hierarchy = 'actioned_at'

    fieldsets = (
        ('Action Information', {
            'fields': ('approval_request', 'actor', 'action', 'comment')
        }),
        ('Security', {
            'fields': ('ip_address',)
        }),
        ('Timestamps', {
            'fields': ('actioned_at', 'created_at', 'updated_at')
        }),
    )

    def action_badge(self, obj):
        """Display action as colored badge."""
        colors = {
            'approve': 'green',
            'reject': 'red',
            'comment': 'blue',
            'request_changes': 'orange'
        }
        color = colors.get(obj.action, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_action_display()
        )
    action_badge.short_description = 'Action'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for notifications."""
    list_display = [
        'id', 'title', 'recipient', 'notification_type',
        'priority_badge', 'is_read_badge', 'sent_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'is_sent', 'sent_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['sent_at', 'read_at', 'created_at', 'updated_at']
    date_hierarchy = 'sent_at'

    fieldsets = (
        ('Notification Information', {
            'fields': ('recipient', 'notification_type', 'title', 'message', 'priority')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id', 'action_url')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_sent', 'sent_at', 'expires_at')
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def priority_badge(self, obj):
        """Display priority as colored badge."""
        colors = {
            'low': 'gray',
            'medium': 'blue',
            'high': 'red'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def is_read_badge(self, obj):
        """Display read status."""
        if obj.is_read:
<<<<<<< HEAD
            return format_html('<span style="color: green;"> Read</span>')
        return format_html('<span style="color: orange;">� Unread</span>')
=======
            return format_html('<span style="color: green;">✓  Read</span>')
        return format_html('<span style="color: orange;">● Unread</span>')
>>>>>>> origin/claude/fix-approval-app-errors-Bwqp5
    is_read_badge.short_description = 'Read Status'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        count = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                count += 1
        self.message_user(request, f'{count} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notification(s) marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'
