"""
Signals for Communication app.
Handles notice publish, event notifications, and bulk message processing.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Notice, NotificationRule, Event, BulkMessage, MessageLog
from .tasks import process_bulk_message


@receiver(post_save, sender=Notice)
def notice_post_save(sender, instance, created, **kwargs):
    if instance.is_published:
        NotificationRule.objects.get_or_create(
            college=instance.college,
            name=f"Notice: {instance.title}",
            event_type='notice_published',
            channels='email,sms',
            template=None,
            defaults={
                'created_by': instance.created_by,
                'updated_by': instance.updated_by,
            }
        )
        print(f"[Communication] Notice '{instance.title}' published.")


@receiver(post_save, sender=Event)
def event_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"[Communication] Event '{instance.title}' created for {instance.event_date}.")


@receiver(post_save, sender=BulkMessage)
def bulk_message_post_save(sender, instance, created, **kwargs):
    if created:
        # Create a placeholder log for the creator if available
        if instance.created_by:
            MessageLog.objects.create(
                bulk_message=instance,
                recipient=instance.created_by,
                message_type=instance.message_type,
                phone_email=getattr(instance.created_by, 'email', '') or getattr(instance.created_by, 'phone', ''),
                message=instance.title,
                status='pending',
                created_by=instance.created_by,
                updated_by=instance.updated_by,
            )

    # Queue processing when status set to pending/ready
    if instance.status in ['pending', 'ready']:
        apply_async = getattr(process_bulk_message, 'apply_async', None)
        if callable(apply_async):
            apply_async(args=[instance.id], eta=instance.scheduled_at)
        else:
            # Fallback synchronous processing
            process_bulk_message(instance.id)
