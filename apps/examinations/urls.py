"""
URL configuration for Examinations app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarksGradeViewSet,
    ExamTypeViewSet,
    ExamViewSet,
    ExamScheduleViewSet,
    ExamAttendanceViewSet,
    AdmitCardViewSet,
    MarksRegisterViewSet,
    StudentMarksViewSet,
    ExamResultViewSet,
    ProgressCardViewSet,
    MarkSheetViewSet,
    TabulationSheetViewSet,
)

router = DefaultRouter()
router.register(r'marks-grades', MarksGradeViewSet, basename='marksgrade')
router.register(r'exam-types', ExamTypeViewSet, basename='examtype')
router.register(r'exams', ExamViewSet, basename='exam')
router.register(r'exam-schedules', ExamScheduleViewSet, basename='examschedule')
router.register(r'exam-attendance', ExamAttendanceViewSet, basename='examattendance')
router.register(r'admit-cards', AdmitCardViewSet, basename='admitcard')
router.register(r'marks-registers', MarksRegisterViewSet, basename='marksregister')
router.register(r'student-marks', StudentMarksViewSet, basename='studentmarks')
router.register(r'exam-results', ExamResultViewSet, basename='examresult')
router.register(r'progress-cards', ProgressCardViewSet, basename='progresscard')
router.register(r'mark-sheets', MarkSheetViewSet, basename='marksheet')
router.register(r'tabulation-sheets', TabulationSheetViewSet, basename='tabulationsheet')

urlpatterns = [
    path('', include(router.urls)),
]
