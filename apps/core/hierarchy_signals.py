"""Signals for organizational hierarchy auto-assignment and permission sync."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import OrganizationNode, RolePermission, HierarchyUserRole
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
    user_ids = HierarchyUserRole.objects.filter(
        role=instance.role,
        is_active=True
    ).values_list('user_id', flat=True)

    for user_id in user_ids:
        PermissionChecker.clear_user_cache(user_id)


@receiver(post_save, sender=HierarchyUserRole)
def clear_user_permission_cache_on_role_change(sender, instance, **kwargs):
    """Clear permission cache when user role changes."""
    PermissionChecker.clear_user_cache(instance.user_id)


@receiver(post_save, sender=get_user_model())
def invalidate_tree_cache_on_user_change(sender, instance, **kwargs):
    """Clear organization tree cache when user is created or updated."""
    cache.delete_pattern('org_tree_*')
    cache.delete_pattern('roles_summary_*')


@receiver(post_delete, sender=get_user_model())
def invalidate_tree_cache_on_user_delete(sender, instance, **kwargs):
    """Clear organization tree cache when user is deleted."""
    cache.delete_pattern('org_tree_*')
    cache.delete_pattern('roles_summary_*')
