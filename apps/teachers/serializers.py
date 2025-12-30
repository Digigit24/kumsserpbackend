"""
DRF Serializers for Teachers app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Teacher, StudyMaterial, Assignment, AssignmentSubmission,
    Homework, HomeworkSubmission
)

User = get_user_model()


# ============================================================================
# BASE SERIALIZERS
# ============================================================================


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for nested representations."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields


class TenantAuditMixin(serializers.Serializer):
    """Mixin to include audit fields in serializers."""
    created_by = UserBasicSerializer(read_only=True)
    updated_by = UserBasicSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# ============================================================================
# TEACHER SERIALIZERS
# ============================================================================


class TeacherListSerializer(serializers.ModelSerializer):
    """Serializer for listing teachers (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.short_name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'phone',
            'college', 'college_name', 'faculty', 'faculty_name',
            'specialization', 'is_active'
        ]
        read_only_fields = ['id', 'full_name', 'college_name', 'faculty_name']


class TeacherSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Teacher model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_details = UserBasicSerializer(source='user', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'id', 'user', 'user_details', 'college', 'college_name',
            'employee_id', 'joining_date', 'faculty', 'faculty_name',
            'first_name', 'middle_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'email', 'phone', 'alternate_phone',
            'address', 'photo', 'specialization',
            'qualifications', 'experience_details', 'custom_attributes',
            'is_active', 'resignation_date',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'college_name', 'faculty_name', 'user_details',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# STUDY MATERIAL SERIALIZERS
# ============================================================================


class StudyMaterialListSerializer(serializers.ModelSerializer):
    """Serializer for listing study materials (minimal fields)."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.short_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'title', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_obj', 'class_name', 'content_type', 'upload_date', 'view_count', 'is_active'
        ]
        read_only_fields = ['id', 'teacher_name', 'subject_name', 'class_name', 'upload_date']


class StudyMaterialSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for StudyMaterial model."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = StudyMaterial
        fields = [
            'id', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_obj', 'class_name', 'section', 'section_name',
            'title', 'description', 'content_type', 'file', 'external_url',
            'topic', 'tags', 'upload_date', 'view_count', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name', 'subject_name', 'class_name', 'section_name',
            'upload_date', 'view_count', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# ASSIGNMENT SERIALIZERS
# ============================================================================


class AssignmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing assignments (minimal fields)."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.short_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_obj', 'class_name', 'assigned_date', 'due_date', 'max_marks', 'is_active'
        ]
        read_only_fields = ['id', 'teacher_name', 'subject_name', 'class_name', 'assigned_date']


class AssignmentSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Assignment model."""
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all_colleges(),
        required=False,
        help_text="Teacher ID (integer). If not provided, will use logged-in teacher's ID."
    )
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_obj', 'class_name', 'section', 'section_name',
            'title', 'description', 'assignment_file', 'assigned_date', 'due_date',
            'max_marks', 'allow_late_submission', 'late_submission_penalty', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name', 'subject_name', 'class_name', 'section_name',
            'assigned_date', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]

    def validate_teacher(self, value):
        """
        Validate teacher field and provide helpful error messages.
        """
        if value is None:
            raise serializers.ValidationError(
                "Teacher ID is required. Please provide the teacher's integer ID (not the user UUID)."
            )

        # Check if teacher exists and is active
        try:
            teacher = Teacher.objects.all_colleges().get(id=value.id, is_active=True)
        except Teacher.DoesNotExist:
            raise serializers.ValidationError(
                f"Teacher with ID {value.id} does not exist or is not active."
            )

        return value

    def validate(self, attrs):
        """
        Validate assignment data and auto-populate teacher if not provided.
        """
        request = self.context.get('request')

        # If teacher is not provided and user is a teacher, use their teacher_id
        if not attrs.get('teacher') and request and hasattr(request.user, 'teacher_profile'):
            try:
                teacher = Teacher.objects.all_colleges().get(
                    user=request.user,
                    is_active=True
                )
                attrs['teacher'] = teacher
            except Teacher.DoesNotExist:
                raise serializers.ValidationError({
                    'teacher': 'Could not find an active teacher profile for the logged-in user. Please provide a teacher ID.'
                })

        # Validate due_date is in the future
        if attrs.get('due_date'):
            from django.utils import timezone
            if attrs['due_date'] < timezone.now().date():
                raise serializers.ValidationError({
                    'due_date': 'Due date must be in the future.'
                })

        return super().validate(attrs)


# ============================================================================
# ASSIGNMENT SUBMISSION SERIALIZERS
# ============================================================================


class AssignmentSubmissionListSerializer(serializers.ModelSerializer):
    """Serializer for listing assignment submissions (minimal fields)."""
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name',
            'submission_date', 'status', 'marks_obtained', 'is_late'
        ]
        read_only_fields = ['id', 'assignment_title', 'student_name', 'submission_date']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """Full serializer for AssignmentSubmission model."""
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.get_full_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name',
            'submission_date', 'submission_file', 'submission_text', 'status',
            'marks_obtained', 'feedback', 'graded_by', 'graded_by_name',
            'graded_date', 'is_late', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'assignment_title', 'student_name', 'graded_by_name',
            'submission_date', 'created_at', 'updated_at'
        ]


# ============================================================================
# HOMEWORK SERIALIZERS
# ============================================================================


class HomeworkListSerializer(serializers.ModelSerializer):
    """Serializer for listing homework (minimal fields)."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.short_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = Homework
        fields = [
            'id', 'title', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_obj', 'class_name', 'assigned_date', 'due_date', 'is_active'
        ]
        read_only_fields = ['id', 'teacher_name', 'subject_name', 'class_name', 'assigned_date']


class HomeworkSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Homework model."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Homework
        fields = [
            'id', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'class_obj', 'class_name', 'section', 'section_name',
            'title', 'description', 'attachment', 'assigned_date', 'due_date', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name', 'subject_name', 'class_name', 'section_name',
            'assigned_date', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# HOMEWORK SUBMISSION SERIALIZERS
# ============================================================================


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for HomeworkSubmission model."""
    homework_title = serializers.CharField(source='homework.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    checked_by_name = serializers.CharField(source='checked_by.get_full_name', read_only=True)

    class Meta:
        model = HomeworkSubmission
        fields = [
            'id', 'homework', 'homework_title', 'student', 'student_name',
            'status', 'completion_date', 'remarks',
            'checked_by', 'checked_by_name', 'checked_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'homework_title', 'student_name', 'checked_by_name',
            'created_at', 'updated_at'
        ]


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
