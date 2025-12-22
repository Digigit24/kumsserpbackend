from django.contrib import admin

from .models import (
    QuestionBank,
    Question,
    QuestionOption,
    OnlineExam,
    ExamQuestion,
    StudentExamAttempt,
    StudentAnswer,
)


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'college', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('college', 'subject', 'is_active')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'bank', 'question_type', 'marks', 'is_active')
    search_fields = ('question_text',)
    list_filter = ('question_type', 'bank', 'is_active')


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'option_text', 'is_correct', 'is_active')
    list_filter = ('is_correct', 'is_active')


@admin.register(OnlineExam)
class OnlineExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'class_obj', 'section', 'start_datetime', 'end_datetime', 'is_published', 'is_active')
    list_filter = ('subject', 'class_obj', 'section', 'is_published', 'is_active')
    search_fields = ('name',)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question', 'marks', 'order', 'is_active')
    list_filter = ('exam', 'is_active')


@admin.register(StudentExamAttempt)
class StudentExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'status', 'start_time', 'end_time', 'is_active')
    list_filter = ('status', 'is_active')


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'marks_awarded', 'is_active')
    list_filter = ('is_correct', 'is_active')
