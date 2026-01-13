from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet
from .models import (
    QuestionBank,
    Question,
    QuestionOption,
    OnlineExam,
    ExamQuestion,
    StudentExamAttempt,
    StudentAnswer,
)
from .serializers import (
    QuestionBankSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
    OnlineExamSerializer,
    ExamQuestionSerializer,
    StudentExamAttemptSerializer,
    StudentAnswerSerializer,
)


class QuestionBankViewSet(CollegeScopedModelViewSet):
    queryset = QuestionBank.objects.all_colleges()
    serializer_class = QuestionBankSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['name']


class QuestionViewSet(RelatedCollegeScopedModelViewSet):
    queryset = Question.objects.select_related('bank')
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bank', 'question_type', 'difficulty_level', 'is_active']
    search_fields = ['question_text']
    ordering_fields = ['created_at', 'marks']
    ordering = ['-created_at']
    related_college_lookup = 'bank__college_id'


class QuestionOptionViewSet(RelatedCollegeScopedModelViewSet):
    queryset = QuestionOption.objects.select_related('question__bank')
    serializer_class = QuestionOptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['question', 'is_active', 'is_correct']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    related_college_lookup = 'question__bank__college_id'


class OnlineExamViewSet(CollegeScopedModelViewSet):
    queryset = OnlineExam.objects.all_colleges()
    serializer_class = OnlineExamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'class_obj', 'section', 'is_published', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['start_datetime', 'end_datetime', 'created_at']
    ordering = ['-start_datetime']


class ExamQuestionViewSet(RelatedCollegeScopedModelViewSet):
    queryset = ExamQuestion.objects.select_related('exam', 'question__bank')
    serializer_class = ExamQuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'question', 'is_active']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    related_college_lookup = 'exam__college_id'


class StudentExamAttemptViewSet(RelatedCollegeScopedModelViewSet):
    queryset = StudentExamAttempt.objects.select_related('exam', 'student')
    serializer_class = StudentExamAttemptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'student', 'status', 'is_active']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']
    related_college_lookup = 'exam__college_id'


class StudentAnswerViewSet(RelatedCollegeScopedModelViewSet):
    queryset = StudentAnswer.objects.select_related('attempt__exam', 'question__bank', 'selected_option')
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['attempt', 'question', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    related_college_lookup = 'attempt__exam__college_id'
