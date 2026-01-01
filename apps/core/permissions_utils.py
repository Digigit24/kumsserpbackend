"""
Permission checking utilities and decorators.
Use these to enforce role-based permissions on API endpoints.
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import Permission


def get_user_college(user):
    """Get the college associated with a user."""
    if hasattr(user, 'college') and user.college:
        return user.college
    elif hasattr(user, 'student_profile') and user.student_profile:
        return user.student_profile.college
    elif hasattr(user, 'teacher_profile') and user.teacher_profile:
        return user.teacher_profile.college
    return None


def get_user_role(user):
    """Determine the user's role."""
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return 'superadmin'
    elif hasattr(user, 'student_profile') and user.student_profile:
        return 'student'
    elif hasattr(user, 'teacher_profile') and user.teacher_profile:
        return 'teacher'
    elif hasattr(user, 'role'):
        return user.role
    return 'student'  # Default


def check_permission(user, module, action):
    """
    Check if a user has permission for a specific action on a module.

    Args:
        user: User instance
        module: Module name (e.g., 'students', 'attendance')
        action: Action to check ('create', 'read', 'update', 'delete')

    Returns:
        bool: True if user has permission, False otherwise
    """
    # Superadmins always have all permissions
    role = get_user_role(user)
    if role == 'superadmin':
        return True

    college = get_user_college(user)
    if not college:
        return False

    try:
        permission = Permission.objects.get(
            college=college,
            role=role,
            is_active=True
        )

        module_perms = permission.permissions_json.get(module, {})
        return module_perms.get(action, False)

    except Permission.DoesNotExist:
        # Use default permissions
        return _get_default_permission(role, module, action)


def _get_default_permission(role, module, action):
    """Get default permission for a role/module/action combination."""
    defaults = {
        'student': {
            'students': ['read'],
            'attendance': ['read'],
            'examinations': ['read'],
            'fees': ['read'],
            'library': ['read'],
        },
        'teacher': {
            'students': ['read', 'update'],
            'classes': ['read', 'update'],
            'subjects': ['read'],
            'attendance': ['create', 'read', 'update'],
            'examinations': ['create', 'read', 'update'],
            'library': ['read'],
        },
        'admin': {
            'students': ['create', 'read', 'update', 'delete'],
            'classes': ['create', 'read', 'update', 'delete'],
            'subjects': ['create', 'read', 'update', 'delete'],
            'attendance': ['create', 'read', 'update', 'delete'],
            'examinations': ['create', 'read', 'update', 'delete'],
            'fees': ['create', 'read', 'update', 'delete'],
            'library': ['create', 'read', 'update', 'delete'],
            'hr': ['create', 'read', 'update', 'delete'],
            'accounting': ['create', 'read', 'update', 'delete'],
            'reports': ['read'],
        },
    }

    role_perms = defaults.get(role, {})
    allowed_actions = role_perms.get(module, [])
    return action in allowed_actions


def require_permission(module, action):
    """
    Decorator to require specific permission for a view.

    Usage:
        @require_permission('students', 'read')
        def my_view(request):
            ...

        @require_permission('attendance', 'create')
        @action(detail=False, methods=['post'])
        def mark_attendance(self, request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request_or_self, *args, **kwargs):
            # Handle both function-based views and class-based views
            if hasattr(request_or_self, 'request'):
                # Class-based view (ViewSet)
                request = request_or_self.request
            else:
                # Function-based view
                request = request_or_self

            user = request.user

            # Check if user is authenticated
            if not user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Check permission
            has_perm = check_permission(user, module, action)

            if not has_perm:
                role = get_user_role(user)
                return Response(
                    {
                        'error': 'Permission denied',
                        'detail': f'Your role ({role}) does not have {action} permission for {module}',
                        'required_permission': f'{module}.{action}'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Call the original view
            return view_func(request_or_self, *args, **kwargs)

        return wrapped_view
    return decorator


class HasPermission:
    """
    DRF permission class to check module/action permissions.

    Usage in ViewSet:
        class StudentViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasPermission]
            permission_module = 'students'

            def get_permission_action(self):
                action_map = {
                    'list': 'read',
                    'retrieve': 'read',
                    'create': 'create',
                    'update': 'update',
                    'partial_update': 'update',
                    'destroy': 'delete',
                }
                return action_map.get(self.action, 'read')
    """

    def has_permission(self, request, view):
        """Check if user has permission for the view."""
        if not request.user.is_authenticated:
            return False

        # Get module from view
        module = getattr(view, 'permission_module', None)
        if not module:
            # If no module specified, allow access (backward compatible)
            return True

        # Get action from view
        if hasattr(view, 'get_permission_action'):
            action = view.get_permission_action()
        else:
            # Default action mapping
            action_map = {
                'list': 'read',
                'retrieve': 'read',
                'create': 'create',
                'update': 'update',
                'partial_update': 'update',
                'destroy': 'delete',
            }
            action = action_map.get(view.action, 'read')

        return check_permission(request.user, module, action)


def get_user_permissions(user):
    """
    Get all permissions for a user.

    Returns:
        dict: Dictionary of all modules and their permissions
    """
    role = get_user_role(user)
    college = get_user_college(user)

    if role == 'superadmin':
        # Superadmins have all permissions
        return {
            'students': {'create': True, 'read': True, 'update': True, 'delete': True},
            'classes': {'create': True, 'read': True, 'update': True, 'delete': True},
            'subjects': {'create': True, 'read': True, 'update': True, 'delete': True},
            'attendance': {'create': True, 'read': True, 'update': True, 'delete': True},
            'examinations': {'create': True, 'read': True, 'update': True, 'delete': True},
            'fees': {'create': True, 'read': True, 'update': True, 'delete': True},
            'library': {'create': True, 'read': True, 'update': True, 'delete': True},
            'hr': {'create': True, 'read': True, 'update': True, 'delete': True},
            'accounting': {'create': True, 'read': True, 'update': True, 'delete': True},
            'reports': {'create': True, 'read': True, 'update': True, 'delete': True},
        }

    if not college:
        return {}

    try:
        permission = Permission.objects.get(
            college=college,
            role=role,
            is_active=True
        )
        return permission.permissions_json

    except Permission.DoesNotExist:
        # Return default permissions
        return _get_default_permissions_dict(role)


def _get_default_permissions_dict(role):
    """Get default permissions dictionary for a role."""
    defaults = {
        'student': {
            'students': {'read': True},
            'attendance': {'read': True},
            'examinations': {'read': True},
            'fees': {'read': True},
            'library': {'read': True},
        },
        'teacher': {
            'students': {'read': True, 'update': True},
            'classes': {'read': True, 'update': True},
            'subjects': {'read': True},
            'attendance': {'create': True, 'read': True, 'update': True},
            'examinations': {'create': True, 'read': True, 'update': True},
            'library': {'read': True},
        },
        'admin': {
            'students': {'create': True, 'read': True, 'update': True, 'delete': True},
            'classes': {'create': True, 'read': True, 'update': True, 'delete': True},
            'subjects': {'create': True, 'read': True, 'update': True, 'delete': True},
            'attendance': {'create': True, 'read': True, 'update': True, 'delete': True},
            'examinations': {'create': True, 'read': True, 'update': True, 'delete': True},
            'fees': {'create': True, 'read': True, 'update': True, 'delete': True},
            'library': {'create': True, 'read': True, 'update': True, 'delete': True},
            'hr': {'create': True, 'read': True, 'update': True, 'delete': True},
            'accounting': {'create': True, 'read': True, 'update': True, 'delete': True},
            'reports': {'read': True},
        },
    }

    return defaults.get(role, {})
