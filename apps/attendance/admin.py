from django.contrib import admin
from .models import (
    StudentAttendance, SubjectAttendance, StaffAttendance, AttendanceNotification
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


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'class_obj', 'section', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'date', 'class_obj', 'section')
    search_fields = ('student__first_name', 'student__last_name', 'student__admission_number')
    date_hierarchy = 'date'

@admin.register(SubjectAttendance)
class SubjectAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_assignment', 'date', 'period', 'status', 'marked_by')
    list_filter = ('status', 'date', 'subject_assignment')
    search_fields = ('student__first_name', 'student__last_name')
    date_hierarchy = 'date'

@admin.register(StaffAttendance)
class StaffAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'check_in_time', 'check_out_time', 'marked_by')
    list_filter = ('status', 'date')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'teacher__employee_id')
    date_hierarchy = 'date'

@admin.register(AttendanceNotification)
class AttendanceNotificationAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'recipient', 'recipient_type', 'notification_type', 'status', 'sent_at')
    list_filter = ('status', 'notification_type', 'recipient_type')
    search_fields = ('attendance__student__first_name', 'attendance__student__last_name', 'recipient__username')
