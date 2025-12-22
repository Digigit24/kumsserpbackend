from django.contrib import admin

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


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'college', 'publish_date', 'is_published', 'is_urgent', 'is_active')
    search_fields = ('title',)
    list_filter = ('college', 'is_published', 'is_urgent', 'is_active')


@admin.register(NoticeVisibility)
class NoticeVisibilityAdmin(admin.ModelAdmin):
    list_display = ('notice', 'target_type', 'class_obj', 'section', 'is_active')
    list_filter = ('target_type', 'is_active')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'college', 'event_date', 'start_time', 'end_time', 'registration_required', 'is_active')
    search_fields = ('title', 'organizer')
    list_filter = ('college', 'event_date', 'registration_required', 'is_active')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registration_date', 'status', 'is_active')
    list_filter = ('status', 'is_active')


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'message_type', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('college', 'message_type', 'is_active')


@admin.register(BulkMessage)
class BulkMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'college', 'message_type', 'status', 'scheduled_at', 'sent_at', 'is_active')
    search_fields = ('title',)
    list_filter = ('college', 'message_type', 'status', 'is_active')


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('bulk_message', 'recipient', 'message_type', 'status', 'sent_at', 'is_active')
    list_filter = ('status', 'message_type', 'is_active')


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'event_type', 'channels', 'is_enabled', 'is_active')
    list_filter = ('college', 'event_type', 'is_enabled', 'is_active')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'is_read', 'is_active')
    list_filter = ('is_read', 'is_active')
