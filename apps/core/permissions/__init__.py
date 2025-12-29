"""
Permission system for KUMSS ERP.
Provides centralized permission management with scope-based access control.
"""
from .registry import PERMISSION_REGISTRY, AVAILABLE_SCOPES, get_default_permissions
from .manager import get_user_permissions, check_permission, get_scope_for_action
from .scope_resolver import get_team_member_ids, apply_scope_filter
from .drf_permissions import IsSuperAdmin, ResourcePermission
from .mixins import ScopedQuerysetMixin

__all__ = [
    'PERMISSION_REGISTRY',
    'AVAILABLE_SCOPES',
    'get_default_permissions',
    'get_user_permissions',
    'check_permission',
    'get_scope_for_action',
    'get_team_member_ids',
    'apply_scope_filter',
    'IsSuperAdmin',
    'ResourcePermission',
    'ScopedQuerysetMixin',
]
