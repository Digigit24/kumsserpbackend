"""Signals for organizational hierarchy auto-assignment and permission sync."""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.cache import cache
from apps.accounts.models import UserRole as AccountUserRole
from .models import OrganizationNode, RolePermission, HierarchyUserRole
from .hierarchy_services import TeamAutoAssignmentService, PermissionChecker


def _clear_hierarchy_cache():
    """Clear all hierarchy-related caches."""
    try:
        # Try to clear specific keys
        cache.delete('org_hierarchy_tree')
        # If using Redis with delete_many or delete_pattern
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern('org_hierarchy_*')
            cache.delete_pattern('user_org_nodes_*')
    except Exception:
        # Silently fail if cache operations fail
        pass


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


@receiver(post_save, sender=HierarchyUserRole)
def invalidate_tree_cache_on_hierarchy_role_change(sender, instance, **kwargs):
    """Clear organization tree cache when hierarchy role is assigned/updated."""
    _clear_hierarchy_cache()


@receiver(post_delete, sender=HierarchyUserRole)
def invalidate_tree_cache_on_hierarchy_role_delete(sender, instance, **kwargs):
    """Clear organization tree cache when hierarchy role is deleted."""
    _clear_hierarchy_cache()


@receiver(post_save, sender=AccountUserRole)
def invalidate_tree_cache_on_account_role_change(sender, instance, **kwargs):
    """Clear organization tree cache when account role is assigned/updated."""
    _clear_hierarchy_cache()


@receiver(post_delete, sender=AccountUserRole)
def invalidate_tree_cache_on_account_role_delete(sender, instance, **kwargs):
    """Clear organization tree cache when account role is deleted."""
    _clear_hierarchy_cache()


@receiver(post_save, sender=get_user_model())
def invalidate_tree_cache_on_user_change(sender, instance, **kwargs):
    """Clear organization tree cache when user is created or updated."""
    _clear_hierarchy_cache()


@receiver(post_delete, sender=get_user_model())
def invalidate_tree_cache_on_user_delete(sender, instance, **kwargs):
    """Clear organization tree cache when user is deleted."""
    _clear_hierarchy_cache()
