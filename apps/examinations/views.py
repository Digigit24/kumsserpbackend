from rest_framework import filters, viewsets
from apps.core.cache_mixins import CachedReadOnlyMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedModelViewSet
from .models import (
    MarksGrade,
    ExamType,
    Exam,
    ExamSchedule,
    ExamAttendance,
    AdmitCard,
    MarksRegister,
    StudentMarks,
    ExamResult,
    ProgressCard,
    MarkSheet,
    TabulationSheet,
)
from .serializers import (
    MarksGradeSerializer,
    ExamTypeSerializer,
    ExamSerializer,
    ExamScheduleSerializer,
    ExamAttendanceSerializer,
    AdmitCardSerializer,
    MarksRegisterSerializer,
    StudentMarksSerializer,
    ExamResultSerializer,
    ProgressCardSerializer,
    MarkSheetSerializer,
    TabulationSheetSerializer,
)


class MarksGradeViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    queryset = MarksGrade.objects.all_colleges()
    serializer_class = MarksGradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'grade']
    ordering_fields = ['grade', 'min_percentage', 'max_percentage']
    ordering = ['grade']


class ExamTypeViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    queryset = ExamType.objects.all_colleges()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']


class ExamViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    queryset = Exam.objects.all_colleges()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['exam_type', 'class_obj', 'academic_session', 'is_published', 'is_active']
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'name']
    ordering = ['-start_date']


class ExamScheduleViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'subject', 'date', 'is_active']
    ordering_fields = ['date', 'start_time']
    ordering = ['date']


class ExamAttendanceViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = ExamAttendance.objects.all()
    serializer_class = ExamAttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam_schedule', 'student', 'status', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class AdmitCardViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = AdmitCard.objects.all()
    serializer_class = AdmitCardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'is_active']
    search_fields = ['card_number']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']


class MarksRegisterViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = MarksRegister.objects.all()
    serializer_class = MarksRegisterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'subject', 'section', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class StudentMarksViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = StudentMarks.objects.all()
    serializer_class = StudentMarksSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['register', 'student', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class ExamResultViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = ExamResult.objects.all()
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'result_status', 'is_active']
    ordering_fields = ['percentage', 'created_at']
    ordering = ['-percentage']


class ProgressCardViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = ProgressCard.objects.all()
    serializer_class = ProgressCardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'is_active']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']


class MarkSheetViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = MarkSheet.objects.all()
    serializer_class = MarkSheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'is_active']
    search_fields = ['sheet_number']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']


class TabulationSheetViewSet(CachedReadOnlyMixin, viewsets.ModelViewSet):
    queryset = TabulationSheet.objects.all()
    serializer_class = TabulationSheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'class_obj', 'section', 'is_active']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']
