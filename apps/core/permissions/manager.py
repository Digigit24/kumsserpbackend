"""
Permission manager for KUMSS permission system.
Handles permission checking and retrieval.
"""
from django.contrib.auth import get_user_model
from apps.core.permissions.registry import get_default_permissions, PERMISSION_REGISTRY

User = get_user_model()


def get_user_permissions(user, college=None):
    """
    Returns merged permission JSON for a user.
    Superadmins get all permissions with 'all' scope.

    Args:
        user: User instance
        college: College instance (optional)

    Returns:
        dict: Permission configuration
    """
    # Superadmin has all permissions
    if getattr(user, 'is_superadmin', False):
        return {
            resource: {
                action: {'scope': 'all', 'enabled': True}
                for action in config['actions']
            }
            for resource, config in PERMISSION_REGISTRY.items()
        }

    # Get user's role from user_type field
    role = getattr(user, 'user_type', 'student')

    # Map UserType to permission role names
    role_mapping = {
        'super_admin': 'admin',
        'college_admin': 'college_admin',
        'teacher': 'teacher',
        'student': 'student',
        'parent': 'student',  # Parents have same permissions as students
        'staff': 'staff',
        'store_manager': 'store_manager',
    }

    role = role_mapping.get(role, 'student')

    # Get college-specific permissions if available
    if college:
        from apps.core.models import Permission
        try:
            perm = Permission.objects.get(college=college, role=role, is_active=True)
            return perm.permissions_json
        except Permission.DoesNotExist:
            pass

    # Fallback to defaults
    return get_default_permissions(role)


def check_permission(user, resource, action, college=None):
    """
    Check if user has permission for resource+action.

    Args:
        user: User instance
        resource: Resource name (e.g., 'attendance')
        action: Action name (e.g., 'create')
        college: College instance (optional)

    Returns:
        tuple: (has_permission: bool, scope: str)
    """
    # Superadmin always has permission
    if getattr(user, 'is_superadmin', False):
        return True, 'all'

    permissions = get_user_permissions(user, college)

    if resource not in permissions:
        return False, 'none'

    if action not in permissions[resource]:
        return False, 'none'

    perm_config = permissions[resource][action]
    enabled = perm_config.get('enabled', False)
    scope = perm_config.get('scope', 'none')

    return enabled, scope


def get_scope_for_action(user, resource, action, college=None):
    """
    Returns the scope for a specific action.

    Args:
        user: User instance
        resource: Resource name
        action: Action name
        college: College instance (optional)

    Returns:
        str: Scope ('none', 'mine', 'team', 'department', 'all')
    """
    has_perm, scope = check_permission(user, resource, action, college)
    return scope if has_perm else 'none'
