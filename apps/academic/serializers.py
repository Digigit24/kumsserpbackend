"""
DRF Serializers for Academic app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Faculty, Program, Class, Section, Subject, OptionalSubject,
    SubjectAssignment, Classroom, ClassTime, Timetable, LabSchedule, ClassTeacher
)
from apps.core.models import College, AcademicSession
from apps.core.serializers import UserBasicSerializer, TenantAuditMixin

User = get_user_model()


# ============================================================================
# FACULTY SERIALIZERS
# ============================================================================


class FacultyListSerializer(serializers.ModelSerializer):
    """Serializer for listing faculties (minimal fields)."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    hod_name = serializers.CharField(source='hod.get_full_name', read_only=True)

    class Meta:
        model = Faculty
        fields = ['id', 'code', 'name', 'short_name', 'college', 'college_name', 'hod', 'hod_name', 'is_active']
        read_only_fields = ['id', 'college_name', 'hod_name']


class FacultySerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Faculty model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    hod_details = UserBasicSerializer(source='hod', read_only=True)

    class Meta:
        model = Faculty
        fields = [
            'id', 'college', 'college_name', 'code', 'name', 'short_name',
            'description', 'hod', 'hod_details', 'display_order', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'hod_details', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# PROGRAM SERIALIZERS
# ============================================================================


class ProgramListSerializer(serializers.ModelSerializer):
    """Serializer for listing programs (minimal fields)."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.short_name', read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'code', 'name', 'short_name', 'college', 'college_name', 'faculty', 'faculty_name', 'program_type', 'is_active']
        read_only_fields = ['id', 'college_name', 'faculty_name']


class ProgramSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Program model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)

    class Meta:
        model = Program
        fields = [
            'id', 'college', 'college_name', 'faculty', 'faculty_name',
            'code', 'name', 'short_name', 'program_type', 'duration', 'duration_type',
            'total_credits', 'description', 'display_order', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'faculty_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# CLASS SERIALIZERS
# ============================================================================


class ClassListSerializer(serializers.ModelSerializer):
    """Serializer for listing classes (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    program_name = serializers.CharField(source='program.short_name', read_only=True)
    session_name = serializers.CharField(source='academic_session.name', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'college', 'college_name', 'program', 'program_name', 'academic_session', 'session_name', 'semester', 'year', 'is_active']
        read_only_fields = ['id', 'college_name', 'program_name', 'session_name']


class ClassSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Class model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    session_name = serializers.CharField(source='academic_session.name', read_only=True)

    class Meta:
        model = Class
        fields = [
            'id', 'college', 'college_name', 'program', 'program_name',
            'academic_session', 'session_name', 'name', 'semester', 'year',
            'max_students', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'program_name', 'session_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# SECTION SERIALIZERS
# ============================================================================


class SectionSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for Section model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = Section
        fields = [
            'id', 'class_obj', 'class_name', 'name', 'max_students', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'class_name', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Scope class_obj queryset by college if context provides request
        request = self.context.get('request')
        if request:
            from apps.core.utils import get_current_college_id
            college_id = get_current_college_id()
            if college_id and college_id != 'all':
                # Use all_colleges() first to bypass default manager scoping, then filter
                self.fields['class_obj'].queryset = Class.objects.all_colleges().filter(college_id=college_id)
            elif college_id == 'all':
                # Superuser mode - show all colleges
                self.fields['class_obj'].queryset = Class.objects.all_colleges()


# ============================================================================
# SUBJECT SERIALIZERS
# ============================================================================


class SubjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing subjects (minimal fields)."""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'short_name', 'college', 'college_name', 'subject_type', 'credits', 'is_active']
        read_only_fields = ['id', 'college_name']


class SubjectSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Subject model."""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Subject
        fields = [
            'id', 'college', 'college_name', 'code', 'name', 'short_name',
            'subject_type', 'credits', 'theory_hours', 'practical_hours',
            'max_marks', 'pass_marks', 'description', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# OPTIONAL SUBJECT SERIALIZERS
# ============================================================================


class OptionalSubjectSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for OptionalSubject model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    subjects_list = SubjectListSerializer(source='subjects', many=True, read_only=True)

    class Meta:
        model = OptionalSubject
        fields = [
            'id', 'class_obj', 'class_name', 'name', 'description',
            'subjects', 'subjects_list', 'min_selection', 'max_selection', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'class_name', 'subjects_list', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            from apps.core.utils import get_current_college_id
            college_id = get_current_college_id()
            if college_id and college_id != 'all':
                # Use all_colleges() first to bypass default manager scoping, then filter
                self.fields['class_obj'].queryset = Class.objects.all_colleges().filter(college_id=college_id)
                self.fields['subjects'].queryset = Subject.objects.all_colleges().filter(college_id=college_id)
            elif college_id == 'all':
                self.fields['class_obj'].queryset = Class.objects.all_colleges()
                self.fields['subjects'].queryset = Subject.objects.all_colleges()


# ============================================================================
# SUBJECT ASSIGNMENT SERIALIZERS
# ============================================================================


class SubjectAssignmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing subject assignments (minimal fields)."""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = SubjectAssignment
        fields = ['id', 'subject', 'subject_name', 'class_obj', 'class_name', 'section', 'section_name', 'teacher', 'teacher_name', 'is_optional', 'is_active']
        read_only_fields = ['id', 'subject_name', 'class_name', 'section_name', 'teacher_name']


class SubjectAssignmentSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for SubjectAssignment model."""
    subject_details = SubjectListSerializer(source='subject', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    teacher_details = UserBasicSerializer(source='teacher', read_only=True)
    lab_instructor_details = UserBasicSerializer(source='lab_instructor', read_only=True)

    class Meta:
        model = SubjectAssignment
        fields = [
            'id', 'subject', 'subject_details', 'class_obj', 'class_name',
            'section', 'section_name', 'teacher', 'teacher_details',
            'lab_instructor', 'lab_instructor_details', 'is_optional', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'subject_details', 'class_name', 'section_name', 'teacher_details', 'lab_instructor_details', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            from apps.core.utils import get_current_college_id
            college_id = get_current_college_id()
            if college_id and college_id != 'all':
                # Use all_colleges() first to bypass default manager scoping, then filter
                self.fields['subject'].queryset = Subject.objects.all_colleges().filter(college_id=college_id)
                self.fields['class_obj'].queryset = Class.objects.all_colleges().filter(college_id=college_id)
                self.fields['section'].queryset = Section.objects.filter(class_obj__college_id=college_id)
            elif college_id == 'all':
                self.fields['subject'].queryset = Subject.objects.all_colleges()
                self.fields['class_obj'].queryset = Class.objects.all_colleges()
                self.fields['section'].queryset = Section.objects.all()


# ============================================================================
# CLASSROOM SERIALIZERS
# ============================================================================


class ClassroomListSerializer(serializers.ModelSerializer):
    """Serializer for listing classrooms (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = Classroom
        fields = ['id', 'code', 'name', 'college', 'college_name', 'room_type', 'capacity', 'is_active']
        read_only_fields = ['id', 'college_name']


class ClassroomSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Classroom model."""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Classroom
        fields = [
            'id', 'college', 'college_name', 'code', 'name', 'room_type',
            'building', 'floor', 'capacity', 'has_projector', 'has_ac', 'has_computer', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# CLASS TIME SERIALIZERS
# ============================================================================


class ClassTimeSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for ClassTime model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = ClassTime
        fields = [
            'id', 'college', 'college_name', 'period_number', 'start_time', 'end_time',
            'is_break', 'break_name', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# TIMETABLE SERIALIZERS
# ============================================================================


class TimetableListSerializer(serializers.ModelSerializer):
    """Serializer for listing timetable entries (minimal fields)."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject_assignment.subject.name', read_only=True)
    teacher_name = serializers.CharField(source='subject_assignment.teacher.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    time_slot = serializers.CharField(source='class_time.__str__', read_only=True)

    class Meta:
        model = Timetable
        fields = ['id', 'class_obj', 'class_name', 'section', 'section_name', 'subject_assignment', 'subject_name', 'teacher_name', 'day_of_week', 'class_time', 'time_slot', 'classroom', 'classroom_name', 'effective_from', 'is_active']
        read_only_fields = ['id', 'class_name', 'section_name', 'subject_name', 'teacher_name', 'classroom_name', 'time_slot']


class TimetableSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Timetable model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_details = SubjectListSerializer(source='subject_assignment.subject', read_only=True)
    teacher_details = UserBasicSerializer(source='subject_assignment.teacher', read_only=True)
    classroom_details = ClassroomListSerializer(source='classroom', read_only=True)
    time_details = ClassTimeSerializer(source='class_time', read_only=True)

    class Meta:
        model = Timetable
        fields = [
            'id', 'class_obj', 'class_name', 'section', 'section_name',
            'subject_assignment', 'subject_details', 'teacher_details',
            'day_of_week', 'class_time', 'time_details',
            'classroom', 'classroom_details', 'effective_from', 'effective_to', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'class_name', 'section_name', 'subject_details', 'teacher_details', 'classroom_details', 'time_details', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            from apps.core.utils import get_current_college_id
            college_id = get_current_college_id()
            if college_id and college_id != 'all':
                # Use all_colleges() first to bypass default manager scoping, then filter
                self.fields['class_obj'].queryset = Class.objects.all_colleges().filter(college_id=college_id)
                self.fields['section'].queryset = Section.objects.filter(class_obj__college_id=college_id)
                self.fields['subject_assignment'].queryset = SubjectAssignment.objects.filter(class_obj__college_id=college_id)
                self.fields['class_time'].queryset = ClassTime.objects.all_colleges().filter(college_id=college_id)
                self.fields['classroom'].queryset = Classroom.objects.all_colleges().filter(college_id=college_id)
            elif college_id == 'all':
                self.fields['class_obj'].queryset = Class.objects.all_colleges()
                self.fields['section'].queryset = Section.objects.all()
                self.fields['subject_assignment'].queryset = SubjectAssignment.objects.all()
                self.fields['class_time'].queryset = ClassTime.objects.all_colleges()
                self.fields['classroom'].queryset = Classroom.objects.all_colleges()


# ============================================================================
# LAB SCHEDULE SERIALIZERS
# ============================================================================


class LabScheduleSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for LabSchedule model."""
    section_name = serializers.CharField(source='section.name', read_only=True)
    subject_name = serializers.CharField(source='subject_assignment.subject.name', read_only=True)
    teacher_name = serializers.CharField(source='subject_assignment.teacher.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)

    class Meta:
        model = LabSchedule
        fields = [
            'id', 'subject_assignment', 'subject_name', 'section', 'section_name',
            'teacher_name', 'day_of_week', 'start_time', 'end_time',
            'classroom', 'classroom_name', 'batch_name', 'effective_from', 'effective_to', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'section_name', 'subject_name', 'teacher_name', 'classroom_name', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            from apps.core.utils import get_current_college_id
            college_id = get_current_college_id()
            if college_id and college_id != 'all':
                # Use all_colleges() first to bypass default manager scoping, then filter
                self.fields['subject_assignment'].queryset = SubjectAssignment.objects.filter(class_obj__college_id=college_id)
                self.fields['section'].queryset = Section.objects.filter(class_obj__college_id=college_id)
                self.fields['classroom'].queryset = Classroom.objects.all_colleges().filter(college_id=college_id)
            elif college_id == 'all':
                self.fields['subject_assignment'].queryset = SubjectAssignment.objects.all()
                self.fields['section'].queryset = Section.objects.all()
                self.fields['classroom'].queryset = Classroom.objects.all_colleges()


# ============================================================================
# CLASS TEACHER SERIALIZERS
# ============================================================================


class ClassTeacherSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for ClassTeacher model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    teacher_details = UserBasicSerializer(source='teacher', read_only=True)
    academic_session = serializers.IntegerField(source='class_obj.academic_session.id', read_only=True)
    academic_session_name = serializers.CharField(source='class_obj.academic_session.name', read_only=True)

    class Meta:
        model = ClassTeacher
        fields = [
            'id', 'class_obj', 'class_name', 'section', 'section_name',
            'academic_session', 'academic_session_name',
            'teacher', 'teacher_details', 'assigned_from', 'assigned_to',
            'is_current', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'class_name', 'section_name', 'teacher_details', 'academic_session', 'academic_session_name', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            from apps.core.utils import get_current_college_id
            college_id = get_current_college_id()
            if college_id and college_id != 'all':
                # Use all_colleges() first to bypass default manager scoping, then filter
                self.fields['class_obj'].queryset = Class.objects.all_colleges().filter(college_id=college_id)
                self.fields['section'].queryset = Section.objects.filter(class_obj__college_id=college_id)
            elif college_id == 'all':
                self.fields['class_obj'].queryset = Class.objects.all_colleges()
                self.fields['section'].queryset = Section.objects.all()


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================


class BulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk delete operations."""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of IDs to delete"
    )
