"""
Celery tasks and fallbacks for communication app.
"""
try:
    from celery import shared_task  # type: ignore
except ImportError:  # pragma: no cover
    def shared_task(*dargs, **dkwargs):
        def decorator(func):
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)

            wrapped.apply_async = lambda args=None, kwargs=None, eta=None: func(*(args or []), **(kwargs or {}))
            return wrapped

        if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
            return decorator(dargs[0])
        return decorator

from django.utils import timezone

from .models import BulkMessage, MessageLog


@shared_task
def process_bulk_message(bulk_message_id):
    """
    Process bulk message: send to recipients (placeholder) and update counts.
    """
    try:
        bulk = BulkMessage.objects.get(pk=bulk_message_id)
    except BulkMessage.DoesNotExist:
        return f"BulkMessage {bulk_message_id} not found"

    sent = 0
    failed = 0
    logs = bulk.logs.all()
    for log in logs:
        try:
            log.status = 'sent'
            log.sent_at = timezone.now()
            log.delivered_at = timezone.now()
            log.save(update_fields=['status', 'sent_at', 'delivered_at', 'updated_at'])
            sent += 1
        except Exception as exc:  # pragma: no cover
            log.status = 'failed'
            log.error_message = str(exc)
            log.save(update_fields=['status', 'error_message', 'updated_at'])
            failed += 1

    bulk.sent_count = sent
    bulk.failed_count = failed
    bulk.status = 'completed'
    bulk.sent_at = timezone.now()
    bulk.save(update_fields=['sent_count', 'failed_count', 'status', 'sent_at', 'updated_at'])
    return f"Processed {bulk_message_id}: sent={sent}, failed={failed}"
