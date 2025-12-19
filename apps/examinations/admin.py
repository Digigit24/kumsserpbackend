from django.contrib import admin

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


@admin.register(MarksGrade)
class MarksGradeAdmin(admin.ModelAdmin):
    list_display = ('grade', 'name', 'college', 'min_percentage', 'max_percentage', 'is_active')
    search_fields = ('grade', 'name')
    list_filter = ('college', 'is_active')


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('college', 'is_active')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'class_obj', 'academic_session', 'start_date', 'end_date', 'is_published', 'is_active')
    list_filter = ('exam_type', 'class_obj', 'academic_session', 'is_published', 'is_active')
    search_fields = ('name',)


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'date', 'start_time', 'end_time', 'is_active')
    list_filter = ('exam', 'subject', 'date', 'is_active')


@admin.register(ExamAttendance)
class ExamAttendanceAdmin(admin.ModelAdmin):
    list_display = ('exam_schedule', 'student', 'status', 'is_active')
    list_filter = ('status', 'is_active')


@admin.register(AdmitCard)
class AdmitCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'student', 'exam', 'issue_date', 'is_active')
    search_fields = ('card_number',)
    list_filter = ('is_active',)


@admin.register(MarksRegister)
class MarksRegisterAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'section', 'max_marks', 'pass_marks', 'is_active')
    list_filter = ('exam', 'subject', 'section', 'is_active')


@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = ('register', 'student', 'total_marks', 'grade', 'is_absent', 'is_active')
    list_filter = ('is_absent', 'is_active')


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'percentage', 'grade', 'result_status', 'is_active')
    list_filter = ('result_status', 'is_active')


@admin.register(ProgressCard)
class ProgressCardAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'issue_date', 'is_active')
    list_filter = ('issue_date', 'is_active')


@admin.register(MarkSheet)
class MarkSheetAdmin(admin.ModelAdmin):
    list_display = ('sheet_number', 'student', 'exam', 'issue_date', 'is_active')
    search_fields = ('sheet_number',)
    list_filter = ('is_active',)


@admin.register(TabulationSheet)
class TabulationSheetAdmin(admin.ModelAdmin):
    list_display = ('exam', 'class_obj', 'section', 'issue_date', 'is_active')
    list_filter = ('exam', 'class_obj', 'section', 'is_active')
