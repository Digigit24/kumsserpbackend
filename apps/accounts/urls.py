"""
URL routing for Accounts app API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    RoleViewSet,
    UserRoleViewSet,
    DepartmentViewSet,
    UserProfileViewSet,
)

app_name = 'accounts'

# Router registrations for all account-related viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'user-profiles', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('', include(router.urls)),
]
   