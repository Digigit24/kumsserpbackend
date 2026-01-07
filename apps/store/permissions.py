from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.core.utils import get_current_college_id
from .models import CentralStore


def _is_manager_of_central_store(user):
    if not user or not user.is_authenticated:
        return False
    return CentralStore.objects.filter(manager=user, is_active=True).exists()


def _user_college_id(user):
    try:
        return getattr(user, 'college_id', None)
    except Exception:
        return None


class IsCentralStoreManagerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return request.user.is_superuser or request.user.user_type == 'central_manager'
        return request.user.is_superuser or request.user.user_type == 'central_manager'


class IsCentralStoreManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.user_type == 'central_manager'


class IsCollegeStoreManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        college_id = get_current_college_id() or _user_college_id(request.user)
        return bool(college_id)


class IsCEOOrFinance(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'is_superuser', False) or user.groups.filter(name__in=['CEO', 'Finance']).exists()


class CanApproveIndent(BasePermission):
    """College admin can approve indents for their college"""
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # College admin or super admin can approve
        return user.is_superuser or (hasattr(user, 'college_id') and user.college_id)


class CanReceiveMaterials(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        college_id = get_current_college_id() or _user_college_id(request.user)
        return bool(college_id)


class CanManageCollegeStore(BasePermission):
    """
    Only super_admin, college_admin, or central_store_manager can create/manage college stores
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # Super admin has full access
        if user.is_superuser:
            return True
        
        # Central store manager can manage
        if user.user_type == 'central_manager':
            return True
        
        # College admin can manage stores for their college
        if user.user_type == 'college_admin' and hasattr(user, 'college_id'):
            return True
        
        return False
