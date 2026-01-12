"""
Signal handlers for core app automation and business logic.
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
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
    # Direct college_id
    if hasattr(instance, 'college_id') and instance.college_id:
        return instance.college_id
    # Direct college FK
    if hasattr(instance, 'college') and instance.college:
        return instance.college
    # Through student
    if hasattr(instance, 'student') and instance.student:
        if hasattr(instance.student, 'college_id'):
            return instance.student.college_id
        if hasattr(instance.student, 'college'):
            return instance.student.college
    # Through teacher
    if hasattr(instance, 'teacher') and instance.teacher:
        if hasattr(instance.teacher, 'college_id'):
            return instance.teacher.college_id
        if hasattr(instance.teacher, 'college'):
            return instance.teacher.college
    # Through class_instance
    if hasattr(instance, 'class_instance') and instance.class_instance:
        if hasattr(instance.class_instance, 'college_id'):
            return instance.class_instance.college_id
    # Through current_class
    if hasattr(instance, 'current_class') and instance.current_class:
        if hasattr(instance.current_class, 'college_id'):
            return instance.current_class.college_id
    # Through exam
    if hasattr(instance, 'exam') and instance.exam:
        if hasattr(instance.exam, 'college_id'):
            return instance.exam.college_id
    # User model - use their assigned college
    if instance.__class__.__name__ == 'User' and hasattr(instance, 'college_id'):
        return instance.college_id

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

    # Get user from request context or instance
    request = get_current_request()
    user = None
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
    else:
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

    # Get user from request context or instance
    request = get_current_request()
    user = None
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
    else:
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


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login activity."""
    if hasattr(user, 'college_id') and user.college_id:
        try:
            ActivityLog.objects.create(
                college_id=user.college_id,
                user=user,
                action='login',
                model_name='User',
                object_id=str(user.pk),
                description=f"{user.get_full_name() or user.username} logged in"
            )
        except Exception:
            pass


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout activity."""
    if user and hasattr(user, 'college_id') and user.college_id:
        try:
            ActivityLog.objects.create(
                college_id=user.college_id,
                user=user,
                action='logout',
                model_name='User',
                object_id=str(user.pk),
                description=f"{user.get_full_name() or user.username} logged out"
            )
        except Exception:
            pass


# Import hierarchy signals
from .hierarchy_signals import *  # noqa
