"""
URL configuration for Academic app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FacultyViewSet,
    ProgramViewSet,
    ClassViewSet,
    SectionViewSet,
    SubjectViewSet,
    OptionalSubjectViewSet,
    SubjectAssignmentViewSet,
    ClassroomViewSet,
    ClassTimeViewSet,
    TimetableViewSet,
    LabScheduleViewSet,
    ClassTeacherViewSet,
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'faculties', FacultyViewSet, basename='faculty')
router.register(r'programs', ProgramViewSet, basename='program')
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'optional-subjects', OptionalSubjectViewSet, basename='optionalsubject')
router.register(r'subject-assignments', SubjectAssignmentViewSet, basename='subjectassignment')
router.register(r'classrooms', ClassroomViewSet, basename='classroom')
router.register(r'class-times', ClassTimeViewSet, basename='classtime')
router.register(r'timetable', TimetableViewSet, basename='timetable')
router.register(r'lab-schedules', LabScheduleViewSet, basename='labschedule')
router.register(r'class-teachers', ClassTeacherViewSet, basename='classteacher')

urlpatterns = [
    path('', include(router.urls)),
]
