"""Signals for organizational hierarchy auto-assignment and permission sync."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import OrganizationNode, RolePermission, UserRole
from .hierarchy_services import TeamAutoAssignmentService, PermissionChecker


@receiver(post_save, sender=OrganizationNode)
def create_team_for_node(sender, instance, created, **kwargs):
    """Auto-create team when organization node is created."""
    if created:
        TeamAutoAssignmentService.create_team_for_node(instance)


@receiver(post_save, sender=RolePermission)
def sync_role_permissions(sender, instance, created, **kwargs):
    """
    When role permissions change:
    1. Clear permission cache for all users with this role
    2. Log change for audit
    """
    # Clear cache for all users with this role
    user_ids = UserRole.objects.filter(
        role=instance.role,
        is_active=True
    ).values_list('user_id', flat=True)

    for user_id in user_ids:
        PermissionChecker.clear_user_cache(user_id)


@receiver(post_save, sender=UserRole)
def clear_user_permission_cache_on_role_change(sender, instance, **kwargs):
    """Clear permission cache when user role changes."""
    PermissionChecker.clear_user_cache(instance.user_id)
