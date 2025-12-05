"""
URL configuration for Attendance app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentAttendanceViewSet,
    SubjectAttendanceViewSet,
    StaffAttendanceViewSet,
    AttendanceNotificationViewSet,
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'student-attendance', StudentAttendanceViewSet, basename='studentattendance')
router.register(r'subject-attendance', SubjectAttendanceViewSet, basename='subjectattendance')
router.register(r'staff-attendance', StaffAttendanceViewSet, basename='staffattendance')
router.register(r'notifications', AttendanceNotificationViewSet, basename='attendancenotification')

urlpatterns = [
    path('', include(router.urls)),
]
