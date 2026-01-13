from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet
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


class MarksGradeViewSet(CollegeScopedModelViewSet):
    queryset = MarksGrade.objects.all_colleges()
    serializer_class = MarksGradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'grade']
    ordering_fields = ['grade', 'min_percentage', 'max_percentage']
    ordering = ['grade']


class ExamTypeViewSet(CollegeScopedModelViewSet):
    queryset = ExamType.objects.all_colleges()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']


class ExamViewSet(CollegeScopedModelViewSet):
    queryset = Exam.objects.all_colleges()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['exam_type', 'class_obj', 'academic_session', 'is_published', 'is_active']
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'name']
    ordering = ['-start_date']


class ExamScheduleViewSet(RelatedCollegeScopedModelViewSet):
    queryset = ExamSchedule.objects.select_related('exam', 'subject', 'classroom', 'invigilator')
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'subject', 'date', 'is_active']
    ordering_fields = ['date', 'start_time']
    ordering = ['date']
    related_college_lookup = 'exam__college_id'


class ExamAttendanceViewSet(RelatedCollegeScopedModelViewSet):
    queryset = ExamAttendance.objects.select_related('exam_schedule__exam', 'student')
    serializer_class = ExamAttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam_schedule', 'student', 'status', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    related_college_lookup = 'exam_schedule__exam__college_id'


class AdmitCardViewSet(RelatedCollegeScopedModelViewSet):
    queryset = AdmitCard.objects.select_related('student', 'exam')
    serializer_class = AdmitCardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'is_active']
    search_fields = ['card_number']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']
    related_college_lookup = 'exam__college_id'


class MarksRegisterViewSet(RelatedCollegeScopedModelViewSet):
    queryset = MarksRegister.objects.select_related('exam', 'subject', 'section')
    serializer_class = MarksRegisterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'subject', 'section', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    related_college_lookup = 'exam__college_id'


class StudentMarksViewSet(RelatedCollegeScopedModelViewSet):
    queryset = StudentMarks.objects.select_related('register__exam', 'student')
    serializer_class = StudentMarksSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['register', 'student', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    related_college_lookup = 'register__exam__college_id'


class ExamResultViewSet(RelatedCollegeScopedModelViewSet):
    queryset = ExamResult.objects.select_related('student', 'exam')
    serializer_class = ExamResultSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'result_status', 'is_active']
    ordering_fields = ['percentage', 'created_at']
    ordering = ['-percentage']
    related_college_lookup = 'exam__college_id'


class ProgressCardViewSet(RelatedCollegeScopedModelViewSet):
    queryset = ProgressCard.objects.select_related('student', 'exam')
    serializer_class = ProgressCardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'is_active']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']
    related_college_lookup = 'exam__college_id'


class MarkSheetViewSet(RelatedCollegeScopedModelViewSet):
    queryset = MarkSheet.objects.select_related('student', 'exam')
    serializer_class = MarkSheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'exam', 'is_active']
    search_fields = ['sheet_number']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']
    related_college_lookup = 'exam__college_id'


class TabulationSheetViewSet(RelatedCollegeScopedModelViewSet):
    queryset = TabulationSheet.objects.select_related('exam', 'class_obj', 'section')
    serializer_class = TabulationSheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'class_obj', 'section', 'is_active']
    ordering_fields = ['issue_date']
    ordering = ['-issue_date']
    related_college_lookup = 'exam__college_id'
