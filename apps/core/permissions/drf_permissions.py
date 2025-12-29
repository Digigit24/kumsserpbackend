"""
Django REST Framework permission classes for KUMSS permission system.
"""
from rest_framework.permissions import BasePermission
from apps.core.permissions.manager import check_permission
from apps.core.utils import get_current_college_id


class IsSuperAdmin(BasePermission):
    """
    Permission class for superadmin-only endpoints.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_superadmin', False)


class ResourcePermission(BasePermission):
    """
    Permission class that checks against Permission model.

    ViewSet must define:
    - resource_name: str (e.g., 'attendance')
    - action_permission_map: dict (optional, for custom actions)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superadmin always has permission
        if getattr(request.user, 'is_superadmin', False):
            return True

        # Get resource name from view
        resource = getattr(view, 'resource_name', None)
        if not resource:
            # If no resource_name, deny access
            return False

        # Map DRF action to permission action
        action_map = getattr(view, 'action_permission_map', {
            'list': 'read',
            'retrieve': 'read',
            'create': 'create',
            'update': 'update',
            'partial_update': 'update',
            'destroy': 'delete',
        })

        drf_action = getattr(view, 'action', None)
        if not drf_action:
            # If no action, allow (will be handled by other permissions)
            return True

        permission_action = action_map.get(drf_action, drf_action)

        # Get college
        college = None
        college_id = get_current_college_id()
        if college_id and college_id != 'all':
            from apps.core.models import College
            try:
                college = College.objects.filter(id=college_id).first()
            except Exception:
                pass

        # Check permission
        has_perm, scope = check_permission(request.user, resource, permission_action, college)

        return has_perm

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.
        Ensures users can only access objects within their scope.
        """
        # Superadmin always has permission
        if getattr(request.user, 'is_superadmin', False):
            return True

        # For now, delegate to has_permission
        # Object-level checks can be enhanced based on scope
        return self.has_permission(request, view)
