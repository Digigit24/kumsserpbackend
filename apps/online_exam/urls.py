"""
URL configuration for Online Exam app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuestionBankViewSet,
    QuestionViewSet,
    QuestionOptionViewSet,
    OnlineExamViewSet,
    ExamQuestionViewSet,
    StudentExamAttemptViewSet,
    StudentAnswerViewSet,
)

router = DefaultRouter()
router.register(r'question-banks', QuestionBankViewSet, basename='questionbank')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'question-options', QuestionOptionViewSet, basename='questionoption')
router.register(r'online-exams', OnlineExamViewSet, basename='onlineexam')
router.register(r'exam-questions', ExamQuestionViewSet, basename='examquestion')
router.register(r'student-exam-attempts', StudentExamAttemptViewSet, basename='studentexamattempt')
router.register(r'student-answers', StudentAnswerViewSet, basename='studentanswer')

urlpatterns = [
    path('', include(router.urls)),
]
