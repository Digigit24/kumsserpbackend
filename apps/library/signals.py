"""
Signals for Library app.
Handles inventory updates, fines, and reminder scheduling.
"""
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BookIssue, BookReturn, LibraryFine, IssueStatus
from .tasks import schedule_due_date_reminders


def _adjust_book_availability(book, delta):
    """
    Increment or decrement the available_quantity safely.
    """
    if not book:
        return
    book.available_quantity = max(0, min(book.quantity, book.available_quantity + delta))
    book.save(update_fields=['available_quantity', 'updated_at'])


@receiver(post_save, sender=BookIssue)
def handle_book_issue(sender, instance, created, **kwargs):
    """
    On new issue:
    - Reduce available copies
    - Send notification placeholder
    - Schedule due date reminders
    """
    if not created:
        return

    _adjust_book_availability(instance.book, delta=-1)

    # Notification placeholder
    print(f"[Library] Book '{instance.book}' issued to {instance.member} (due {instance.due_date}).")

    # Schedule reminders (Celery if available, sync fallback otherwise)
    schedule_due_date_reminders(instance.id)


@receiver(post_save, sender=BookReturn)
def handle_book_return(sender, instance, created, **kwargs):
    """
    On return:
    - Increase available copies
    - Calculate fines (late + damage)
    - Update issue status and return date
    """
    issue = instance.issue

    if created:
        _adjust_book_availability(issue.book, delta=1)

    # Update issue status/return date
    if issue:
        updated_fields = []
        if issue.return_date != instance.return_date:
            issue.return_date = instance.return_date
            updated_fields.append('return_date')
        if issue.status != IssueStatus.RETURNED:
            issue.status = IssueStatus.RETURNED
            updated_fields.append('status')
        if updated_fields:
            issue.save(update_fields=updated_fields + ['updated_at'])

    # Compute fine
    fine_total = Decimal(instance.fine_amount or 0) + Decimal(instance.damage_charges or 0)
    if issue and issue.due_date and instance.return_date and instance.return_date > issue.due_date:
        days_late = (instance.return_date - issue.due_date).days
        fine_total += Decimal(days_late) * Decimal('5.00')  # basic per-day fine

    if fine_total > 0 and issue:
        fine, created_fine = LibraryFine.objects.get_or_create(
            member=issue.member,
            book_issue=issue,
            fine_date=instance.return_date,
            defaults={
                'amount': fine_total,
                'reason': f"Late return fine for '{issue.book}'",
                'remarks': instance.remarks,
                'created_by': instance.created_by,
                'updated_by': instance.updated_by,
            },
        )
        if not created_fine and fine.amount != fine_total:
            fine.amount = fine_total
            fine.reason = f"Late/damage fine for '{issue.book}'"
            fine.remarks = instance.remarks
            fine.save(update_fields=['amount', 'reason', 'remarks', 'updated_at'])

    # Placeholder for notifying member about return processing
    print(f"[Library] Return processed for {issue.book} from {issue.member} on {instance.return_date}.")
