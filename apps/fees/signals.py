"""
Signals for Fees app.
Lightweight implementations to avoid breaking tests; replace with full business logic as needed.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone

from .models import (
    FeeCollection,
    FeeReceipt,
    FeeStructure,
    FeeInstallment,
    FeeFine,
    FeeReminder,
)


@receiver(post_save, sender=FeeCollection)
def fee_collection_post_save(sender, instance, created, **kwargs):
    """
    On new collection:
    - Generate a simple receipt if one does not exist.
    - Update fee structures is left as a TODO (no direct relation to structure on model).
    """
    if not created:
        return

    # Create a basic receipt if none exists for this collection
    if not instance.receipts.exists():
        receipt_number = f"RCPT-{instance.pk}"
        FeeReceipt.objects.create(
            collection=instance,
            receipt_number=receipt_number,
            created_by=instance.created_by,
            updated_by=instance.updated_by,
        )

    # TODO: Apply collection to FeeStructure (update paid_amount/balance) when mapping is defined.
    # TODO: Clear pending reminders and send receipt notifications.


@receiver(post_save, sender=FeeStructure)
def fee_structure_post_save(sender, instance, created, **kwargs):
    """
    On new fee structure:
    - Ensure at least one installment exists.
    - Placeholder for scheduling reminders/notifications.
    """
    if not created:
        return

    # Create a single installment covering the full amount if none exist.
    if not instance.installments.exists():
        FeeInstallment.objects.create(
            student=instance.student,
            fee_structure=instance,
            installment_number=1,
            amount=instance.amount,
            due_date=instance.due_date,
            created_by=instance.created_by,
            updated_by=instance.updated_by,
        )

    # Schedule a basic reminder on due date if none exists.
    if not instance.reminders.exists():
        FeeReminder.objects.create(
            student=instance.student,
            fee_structure=instance,
            reminder_date=instance.due_date,
            reminder_type='email',
            status='pending',
            message=f"Fee due on {instance.due_date} for {instance.fee_master}",
            created_by=instance.created_by,
            updated_by=instance.updated_by,
        )

    # TODO: Send notifications to student/parent.


@receiver(post_save, sender=FeeFine)
def fee_fine_post_save(sender, instance, created, **kwargs):
    """
    On new fine:
    - Placeholder for notification or linking to fee structure balance.
    """
    if not created:
        return

    # TODO: Notify student/parent and adjust fee structure balance if applicable.
    # For now, no-op to keep side effects minimal.
    return
