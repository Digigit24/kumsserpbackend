"""
URL configuration for Teachers app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeacherViewSet,
    StudyMaterialViewSet,
    AssignmentViewSet,
    AssignmentSubmissionViewSet,
    HomeworkViewSet,
    HomeworkSubmissionViewSet,
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'study-materials', StudyMaterialViewSet, basename='studymaterial')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'assignment-submissions', AssignmentSubmissionViewSet, basename='assignmentsubmission')
router.register(r'homework', HomeworkViewSet, basename='homework')
router.register(r'homework-submissions', HomeworkSubmissionViewSet, basename='homeworksubmission')

urlpatterns = [
    path('', include(router.urls)),
]
