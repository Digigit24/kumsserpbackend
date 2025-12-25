from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedModelViewSet
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


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bank', 'question_type', 'difficulty_level', 'is_active']
    search_fields = ['question_text']
    ordering_fields = ['created_at', 'marks']
    ordering = ['-created_at']


class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['question', 'is_active', 'is_correct']
    ordering_fields = ['created_at']
    ordering = ['created_at']


class OnlineExamViewSet(CollegeScopedModelViewSet):
    queryset = OnlineExam.objects.all_colleges()
    serializer_class = OnlineExamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'class_obj', 'section', 'is_published', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['start_datetime', 'end_datetime', 'created_at']
    ordering = ['-start_datetime']


class ExamQuestionViewSet(viewsets.ModelViewSet):
    queryset = ExamQuestion.objects.all()
    serializer_class = ExamQuestionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'question', 'is_active']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']


class StudentExamAttemptViewSet(viewsets.ModelViewSet):
    queryset = StudentExamAttempt.objects.all()
    serializer_class = StudentExamAttemptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exam', 'student', 'status', 'is_active']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']


class StudentAnswerViewSet(viewsets.ModelViewSet):
    queryset = StudentAnswer.objects.all()
    serializer_class = StudentAnswerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['attempt', 'question', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['created_at']
