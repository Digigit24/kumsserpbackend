"""
Signal handlers for core app automation and business logic.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import (
    College,
    AcademicYear,
    ActivityLog,
    NotificationSetting,
    Weekend
)
from .utils import get_current_request, get_client_ip


def get_college_from_instance(instance):
    """Extract college from instance for activity logging."""
    if hasattr(instance, 'college_id'):
        return instance.college_id
    elif hasattr(instance, 'college'):
        return instance.college
    elif hasattr(instance, 'student') and hasattr(instance.student, 'college_id'):
        return instance.student.college_id
    return None


def should_log_model(sender):
    """Check if this model should be auto-logged."""
    excluded = ['ActivityLog', 'Session', 'LogEntry', 'ContentType', 'Permission', 'Migration']
    return sender.__name__ not in excluded


@receiver(post_save)
def auto_log_model_changes(sender, instance, created, **kwargs):
    """Automatically log create/update actions for all models."""
    if not should_log_model(sender):
        return

    college = get_college_from_instance(instance)
    if not college:
        return

    user = getattr(instance, 'created_by', None) if created else getattr(instance, 'updated_by', None)
    action = 'create' if created else 'update'

    try:
        ActivityLog.objects.create(
            college_id=college.id if hasattr(college, 'id') else college,
            user=user,
            action=action,
            model_name=sender.__name__,
            object_id=str(instance.pk),
            description=f"{sender.__name__} {action}d: {str(instance)[:100]}"
        )
    except Exception:
        pass


@receiver(post_delete)
def auto_log_model_deletions(sender, instance, **kwargs):
    """Automatically log delete actions for all models."""
    if not should_log_model(sender):
        return

    college = get_college_from_instance(instance)
    if not college:
        return

    user = getattr(instance, 'updated_by', None)

    try:
        ActivityLog.objects.create(
            college_id=college.id if hasattr(college, 'id') else college,
            user=user,
            action='delete',
            model_name=sender.__name__,
            object_id=str(instance.pk),
            description=f"{sender.__name__} deleted: {str(instance)[:100]}"
        )
    except Exception:
        pass


@receiver(post_save, sender=College)
def create_college_defaults(sender, instance, created, **kwargs):
    """
    Automatically create default settings when a new College is created.

    Actions:
    1. Create a NotificationSetting entry for the college
    2. Create Weekend entries for Saturday (5) and Sunday (6)
    """
    if created:
        # Create default notification settings
        NotificationSetting.objects.create(
            college=instance,
            created_by=instance.created_by,
            updated_by=instance.updated_by
        )

        # Create default weekend entries (Saturday and Sunday)
        Weekend.objects.bulk_create([
            Weekend(
                college=instance,
                day=5,  # Saturday
                created_by=instance.created_by,
                updated_by=instance.updated_by
            ),
            Weekend(
                college=instance,
                day=6,  # Sunday
                created_by=instance.created_by,
                updated_by=instance.updated_by
            )
        ])


@receiver(pre_save, sender=AcademicYear)
def enforce_single_current_academic_year(sender, instance, **kwargs):
    """
    Ensure only one AcademicYear is marked as current per college.

    When an AcademicYear is saved with is_current=True, automatically
    set is_current=False for all other years in the same college.
    """
    if instance.is_current:
        # Use select_for_update to prevent race conditions
        with transaction.atomic():
            # Get all other academic years in the same college (excluding current instance)
            other_years = AcademicYear.objects.filter(
                college=instance.college,
                is_current=True
            )

            # Exclude the current instance if it already has an ID (update operation)
            if instance.pk:
                other_years = other_years.exclude(pk=instance.pk)

            # Set is_current=False for all other years
            other_years.update(is_current=False)


@receiver(pre_save, sender=ActivityLog)
def capture_request_context(sender, instance, **kwargs):
    """
    Automatically capture request context for ActivityLog entries.

    Extracts and populates:
    - Client IP address (handles X-Forwarded-For)
    - User agent string
    """
    # Only capture if not already set
    if not instance.ip_address or not instance.user_agent:
        request = get_current_request()

        if request:
            # Capture IP address if not already set
            if not instance.ip_address:
                instance.ip_address = get_client_ip(request)

            # Capture user agent if not already set
            if not instance.user_agent:
                instance.user_agent = request.META.get('HTTP_USER_AGENT', '')
