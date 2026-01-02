"""
DRF Serializers for Teachers app models.
"""
import uuid as uuid_lib
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Teacher, StudyMaterial, Assignment, AssignmentSubmission,
    Homework, HomeworkSubmission
)

User = get_user_model()


# ============================================================================
# CUSTOM FIELDS
# ============================================================================


class FlexibleTeacherField(serializers.PrimaryKeyRelatedField):
    """
    Custom field that accepts Teacher ID (integer), User ID (UUID), or string numbers.
    Automatically converts to the appropriate Teacher instance.
    If lookup fails, returns None and lets validation handle it.
    """

    def to_internal_value(self, data):
        """Convert UUID or string to Teacher instance."""
        if data is None or data == '':
            return None

        # Try to detect if it's a UUID
        if isinstance(data, str) and len(data) == 36 and '-' in data:
            try:
                # It's a UUID - look up teacher by user UUID
                user_uuid = uuid_lib.UUID(data)
                teacher = Teacher.objects.all_colleges().get(user__id=user_uuid, is_active=True)
                return teacher
            except (ValueError, Teacher.DoesNotExist):
                # UUID doesn't match a teacher - return None and let validate() handle it
                return None

        # Try to convert string to integer
        if isinstance(data, str):
            try:
                data = int(data)
            except (ValueError, TypeError):
                return None

        # Try integer lookup
        try:
            return super().to_internal_value(data)
        except:
            return None


# ============================================================================
# BASE SERIALIZERS
# ============================================================================

from apps.core.serializers import UserBasicSerializer, TenantAuditMixin


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
    teacher = FlexibleTeacherField(
        queryset=Teacher.objects.all_colleges(),
        required=False,
        help_text="Teacher ID (integer), User UUID, or string number. Auto-populated if not provided."
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

    def to_internal_value(self, data):
        """
        Convert string IDs to integers before validation.
        Makes the API more forgiving of frontend mistakes.
        """
        # Convert string IDs to integers for non-teacher fields
        for field in ['subject', 'class_obj', 'section', 'max_marks']:
            if field in data and data[field] is not None:
                try:
                    # Convert to integer if it's a string
                    if isinstance(data[field], str):
                        data[field] = int(data[field])
                except (ValueError, TypeError):
                    # If conversion fails, leave as is and let validation handle it
                    pass

        return super().to_internal_value(data)

    def validate_subject(self, value):
        """Validate subject ID."""
        if not value or (hasattr(value, 'id') and value.id == 0):
            raise serializers.ValidationError(
                "Subject is required. Please select a valid subject from the dropdown."
            )
        return value

    def validate_class_obj(self, value):
        """Validate class ID."""
        if not value or (hasattr(value, 'id') and value.id == 0):
            raise serializers.ValidationError(
                "Class is required. Please select a valid class from the dropdown."
            )
        return value

    def validate(self, attrs):
        """
        Validate assignment data and auto-populate teacher if not provided.
        Auto-creates teacher profile if user is a teacher but has no profile.
        """
        request = self.context.get('request')

        # ALWAYS try to get teacher from logged-in user first
        if request and request.user:
            try:
                teacher = Teacher.objects.all_colleges().get(
                    user=request.user,
                    is_active=True
                )
                # Use logged-in user's teacher profile
                attrs['teacher'] = teacher
                attrs['college'] = teacher.college  # Set college for assignment
            except Teacher.DoesNotExist:
                # Teacher profile doesn't exist - auto-create it if user is a teacher
                if request.user.user_type == 'teacher':
                    from apps.core.models import College
                    from django.utils import timezone

                    college = request.user.college or College.objects.first()
                    if college:
                        # Auto-create teacher profile
                        teacher = Teacher.objects.create(
                            user=request.user,
                            college=college,
                            employee_id=f'AUTO{str(request.user.id).replace("-", "")[:12]}',
                            joining_date=timezone.now().date(),
                            first_name=request.user.first_name or request.user.username,
                            last_name=request.user.last_name or 'Teacher',
                            date_of_birth='1990-01-01',
                            gender='Male',
                            email=request.user.email or f'{request.user.username}@example.com',
                            phone='0000000000',
                            is_active=True
                        )
                        attrs['teacher'] = teacher
                        attrs['college'] = college  # Set college for assignment
                    elif not attrs.get('teacher'):
                        raise serializers.ValidationError({
                            'teacher': 'No college found. Cannot create teacher profile.'
                        })
                elif not attrs.get('teacher'):
                    raise serializers.ValidationError({
                        'teacher': 'No teacher profile found. User must be a teacher to create assignments.'
                    })

        # If still no teacher, raise error
        if not attrs.get('teacher'):
            raise serializers.ValidationError({
                'teacher': 'Could not determine teacher. Please ensure you have an active teacher profile.'
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
