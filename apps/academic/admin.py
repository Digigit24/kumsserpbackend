from django.contrib import admin
from .models import (
    Faculty, Program, Class, Section, Subject, OptionalSubject,
    SubjectAssignment, Classroom, ClassTime, Timetable, LabSchedule, ClassTeacher
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


@admin.register(Faculty)
class FacultyAdmin(BaseModelAdmin):
    list_display = ('name', 'code', 'college', 'hod')
    list_filter = ('college',)
    search_fields = ('name', 'code')
    
    def get_queryset(self, request):
        # Use all_colleges to show all faculties regardless of college context
        return Faculty.objects.all_colleges()

@admin.register(Program)
class ProgramAdmin(BaseModelAdmin):
    list_display = ('name', 'code', 'college', 'faculty', 'program_type')
    list_filter = ('college', 'faculty', 'program_type')
    search_fields = ('name', 'code')

@admin.register(Class)
class ClassAdmin(BaseModelAdmin):
    list_display = ('name', 'program', 'semester', 'year', 'college')
    list_filter = ('college', 'program', 'semester')
    search_fields = ('name',)

@admin.register(Section)
class SectionAdmin(BaseModelAdmin):
    list_display = ('name', 'class_obj', 'max_students')
    list_filter = ('class_obj__college',)
    search_fields = ('name', 'class_obj__name')

@admin.register(Subject)
class SubjectAdmin(BaseModelAdmin):
    list_display = ('name', 'code', 'college', 'subject_type', 'credits')
    list_filter = ('college', 'subject_type')
    search_fields = ('name', 'code')

@admin.register(OptionalSubject)
class OptionalSubjectAdmin(BaseModelAdmin):
    list_display = ('name', 'class_obj', 'min_selection', 'max_selection')
    list_filter = ('class_obj__college',)
    search_fields = ('name',)

@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(BaseModelAdmin):
    list_display = ('subject', 'class_obj', 'section', 'teacher')
    list_filter = ('class_obj__college', 'teacher')
    search_fields = ('subject__name', 'teacher__username')

@admin.register(Classroom)
class ClassroomAdmin(BaseModelAdmin):
    list_display = ('name', 'code', 'college', 'room_type', 'capacity')
    list_filter = ('college', 'room_type')
    search_fields = ('name', 'code')

@admin.register(ClassTime)
class ClassTimeAdmin(BaseModelAdmin):
    list_display = ('period_number', 'start_time', 'end_time', 'college', 'is_break')
    list_filter = ('college', 'is_break')

@admin.register(Timetable)
class TimetableAdmin(BaseModelAdmin):
    list_display = ('section', 'day_of_week', 'class_time', 'subject_assignment', 'classroom')
    list_filter = ('section__class_obj__college', 'day_of_week')

@admin.register(LabSchedule)
class LabScheduleAdmin(BaseModelAdmin):
    list_display = ('section', 'day_of_week', 'start_time', 'end_time', 'classroom')
    list_filter = ('section__class_obj__college', 'day_of_week')

@admin.register(ClassTeacher)
class ClassTeacherAdmin(BaseModelAdmin):
    list_display = ('teacher', 'section', 'class_obj', 'is_current')
    list_filter = ('class_obj__college', 'is_current')
