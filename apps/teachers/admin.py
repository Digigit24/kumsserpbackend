from django.contrib import admin
from .models import (
    Teacher, StudyMaterial, Assignment, AssignmentSubmission,
    Homework, HomeworkSubmission
)


class BaseModelAdmin(admin.ModelAdmin):
    """Base admin that bypasses college scoping for superadmin."""
    
    def get_queryset(self, request):
        """Show all records regardless of college context."""
        qs = self.model.objects
        if hasattr(qs, 'all_colleges'):
            return qs.all_colleges()
        return super().get_queryset(request)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Override to show all FK options regardless of college context."""
        if db_field.remote_field and hasattr(db_field.remote_field.model.objects, 'all_colleges'):
            kwargs['queryset'] = db_field.remote_field.model.objects.all_colleges()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'email', 'phone', 'faculty', 'is_active')
    list_filter = ('college', 'faculty', 'is_active', 'gender')
    search_fields = ('first_name', 'last_name', 'employee_id', 'email', 'phone')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'subject', 'class_obj', 'content_type', 'upload_date', 'is_active')
    list_filter = ('content_type', 'is_active', 'upload_date')
    search_fields = ('title', 'description', 'topic', 'tags', 'teacher__first_name', 'teacher__last_name')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'subject', 'class_obj', 'assigned_date', 'due_date', 'max_marks', 'is_active')
    list_filter = ('is_active', 'assigned_date', 'due_date')
    search_fields = ('title', 'description', 'teacher__first_name', 'teacher__last_name')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'submission_date', 'marks_obtained', 'is_late')
    list_filter = ('status', 'is_late', 'submission_date')
    search_fields = ('assignment__title', 'student__first_name', 'student__last_name')

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'subject', 'class_obj', 'assigned_date', 'due_date', 'is_active')
    list_filter = ('is_active', 'assigned_date', 'due_date')
    search_fields = ('title', 'description', 'teacher__first_name', 'teacher__last_name')

@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('homework', 'student', 'status', 'completion_date', 'checked_by')
    list_filter = ('status', 'completion_date')
    search_fields = ('homework__title', 'student__first_name', 'student__last_name')
