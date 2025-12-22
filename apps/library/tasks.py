"""
Celery tasks and scheduling helpers for library due date reminders.
Includes a safe fallback when Celery is not installed.
"""
from datetime import datetime, timedelta

from django.utils import timezone

from .models import BookIssue

try:
    from celery import shared_task  # type: ignore
except ImportError:  # pragma: no cover - fallback when Celery is not available
    def shared_task(*dargs, **dkwargs):
        """
        Lightweight stand-in for Celery's shared_task decorator.
        Supports usage with or without parentheses and adds apply_async stub.
        """
        def decorator(func):
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)

            # Mimic Celery's Task.apply_async interface in a no-op fashion
            wrapped.apply_async = lambda args=None, kwargs=None, eta=None: func(
                *(args or []), **(kwargs or {})
            )
            return wrapped

        # Handle @shared_task without parentheses
        if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
            return decorator(dargs[0])

        return decorator


@shared_task
def send_due_date_reminder(issue_id, stage):
    """
    Send reminder for a book issue based on stage.
    Stages: due_in_3_days, due_tomorrow, overdue
    """
    try:
        issue = BookIssue.objects.select_related('book', 'member').get(pk=issue_id)
    except BookIssue.DoesNotExist:
        return f"Issue {issue_id} not found"

    message_map = {
        'due_in_3_days': f"Reminder: '{issue.book}' is due on {issue.due_date} (3 days left).",
        'due_tomorrow': f"Reminder: '{issue.book}' is due tomorrow ({issue.due_date}).",
        'overdue': f"Overdue: '{issue.book}' was due on {issue.due_date}. Please return immediately.",
    }
    message = message_map.get(stage, f"Reminder for issue {issue_id} ({stage}).")

    # Placeholder - integrate with notification system
    print(f"[LibraryReminder] {message} -> Member {issue.member}")
    return message


def _eta_from_offset(due_date, days_offset):
    target_date = due_date + timedelta(days=days_offset)
    target_dt = datetime.combine(target_date, datetime.min.time())
    if timezone.is_naive(target_dt):
        target_dt = timezone.make_aware(target_dt, timezone.get_current_timezone())
    return target_dt


def schedule_due_date_reminders(issue_id):
    """
    Schedule reminders at -3 days, -1 day, and +1 day relative to due date.
    Falls back to synchronous execution if Celery is unavailable.
    """
    try:
        issue = BookIssue.objects.get(pk=issue_id)
    except BookIssue.DoesNotExist:
        return

    schedule = [
        (-3, 'due_in_3_days'),
        (-1, 'due_tomorrow'),
        (1, 'overdue'),  # 1 day after due date
    ]
    for days_offset, stage in schedule:
        eta = _eta_from_offset(issue.due_date, days_offset)
        apply_async = getattr(send_due_date_reminder, 'apply_async', None)
        if callable(apply_async):
            apply_async(args=[issue.id, stage], eta=eta)
        else:
            # Fallback: run immediately if target time already passed
            if eta.date() <= timezone.now().date():
                send_due_date_reminder(issue.id, stage)
