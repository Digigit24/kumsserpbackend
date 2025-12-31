"""
URL routing for Core app API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CollegeViewSet,
    AcademicYearViewSet,
    AcademicSessionViewSet,
    HolidayViewSet,
    WeekendViewSet,
    SystemSettingViewSet,
    NotificationSettingViewSet,
    ActivityLogViewSet,
    PermissionViewSet,
    TeamMembershipViewSet,
)
from .upload_views import (
    SingleFileUploadView,
    MultipleFileUploadView,
    FileDeleteView,
    PresignedUrlView,
)

app_name = 'core'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'colleges', CollegeViewSet, basename='college')
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')
router.register(r'academic-sessions', AcademicSessionViewSet, basename='academic-session')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'weekends', WeekendViewSet, basename='weekend')
router.register(r'system-settings', SystemSettingViewSet, basename='system-setting')
router.register(r'notification-settings', NotificationSettingViewSet, basename='notification-setting')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'team-memberships', TeamMembershipViewSet, basename='team-membership')

urlpatterns = [
    path('', include(router.urls)),

    # File upload endpoints
    path('upload/single/', SingleFileUploadView.as_view(), name='upload-single'),
    path('upload/multiple/', MultipleFileUploadView.as_view(), name='upload-multiple'),
    path('upload/delete/', FileDeleteView.as_view(), name='upload-delete'),
    path('upload/presigned-url/', PresignedUrlView.as_view(), name='upload-presigned-url'),
]
