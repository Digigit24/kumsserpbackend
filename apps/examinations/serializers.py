"""
DRF Serializers for Examinations app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

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
# MARKS GRADE SERIALIZERS
# ============================================================================


class MarksGradeSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for MarksGrade model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = MarksGrade
        fields = [
            'id', 'college', 'college_name', 'name', 'grade',
            'min_percentage', 'max_percentage', 'grade_point', 'remarks',
            'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# EXAM TYPE SERIALIZERS
# ============================================================================


class ExamTypeSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for ExamType model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = ExamType
        fields = [
            'id', 'college', 'college_name', 'name', 'code', 'description',
            'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# EXAM SERIALIZERS
# ============================================================================


class ExamListSerializer(serializers.ModelSerializer):
    """Serializer for listing exams (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    session_name = serializers.CharField(source='academic_session.name', read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'college', 'college_name', 'name',
            'exam_type', 'exam_type_name',
            'class_obj', 'class_name',
            'academic_session', 'session_name',
            'start_date', 'end_date', 'is_published', 'is_active'
        ]
        read_only_fields = ['id', 'college_name', 'exam_type_name', 'class_name', 'session_name']


class ExamSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Exam model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    session_name = serializers.CharField(source='academic_session.name', read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'college', 'college_name', 'name',
            'exam_type', 'exam_type_name',
            'class_obj', 'class_name',
            'academic_session', 'session_name',
            'start_date', 'end_date', 'is_published', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'exam_type_name', 'class_name', 'session_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# EXAM SCHEDULE SERIALIZERS
# ============================================================================


class ExamScheduleListSerializer(serializers.ModelSerializer):
    """Serializer for listing exam schedules (minimal fields)."""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='subject.short_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    invigilator_name = serializers.CharField(source='invigilator.get_full_name', read_only=True)

    class Meta:
        model = ExamSchedule
        fields = [
            'id', 'exam', 'exam_name', 'subject', 'subject_name',
            'date', 'start_time', 'end_time',
            'classroom', 'classroom_name',
            'invigilator', 'invigilator_name', 'max_marks'
        ]
        read_only_fields = ['id', 'exam_name', 'subject_name', 'classroom_name', 'invigilator_name']


class ExamScheduleSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for ExamSchedule model."""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    invigilator_name = serializers.CharField(source='invigilator.get_full_name', read_only=True)

    class Meta:
        model = ExamSchedule
        fields = [
            'id', 'exam', 'exam_name', 'subject', 'subject_name',
            'date', 'start_time', 'end_time',
            'classroom', 'classroom_name',
            'invigilator', 'invigilator_name', 'max_marks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'exam_name', 'subject_name', 'classroom_name', 'invigilator_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# EXAM ATTENDANCE SERIALIZERS
# ============================================================================


class ExamAttendanceSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for ExamAttendance model."""
    exam_name = serializers.CharField(source='exam_schedule.exam.name', read_only=True)
    subject_name = serializers.CharField(source='exam_schedule.subject.name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = ExamAttendance
        fields = [
            'id', 'exam_schedule', 'exam_name', 'subject_name',
            'student', 'student_name', 'status', 'remarks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'exam_name', 'subject_name', 'student_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# ADMIT CARD SERIALIZERS
# ============================================================================


class AdmitCardSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for AdmitCard model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = AdmitCard
        fields = [
            'id', 'student', 'student_name', 'exam', 'exam_name',
            'card_number', 'issue_date', 'card_file',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'exam_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# MARKS REGISTER SERIALIZERS
# ============================================================================


class MarksRegisterSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for MarksRegister model."""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = MarksRegister
        fields = [
            'id', 'exam', 'exam_name', 'subject', 'subject_name',
            'section', 'section_name', 'max_marks', 'pass_marks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'exam_name', 'subject_name', 'section_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# STUDENT MARKS SERIALIZERS
# ============================================================================


class StudentMarksListSerializer(serializers.ModelSerializer):
    """Serializer for listing student marks (minimal fields)."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='register.exam.name', read_only=True)
    subject_name = serializers.CharField(source='register.subject.name', read_only=True)

    class Meta:
        model = StudentMarks
        fields = [
            'id', 'register', 'student', 'student_name',
            'exam_name', 'subject_name',
            'theory_marks', 'practical_marks', 'internal_marks',
            'total_marks', 'grade', 'is_absent'
        ]
        read_only_fields = ['id', 'student_name', 'exam_name', 'subject_name']


class StudentMarksSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for StudentMarks model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='register.exam.name', read_only=True)
    subject_name = serializers.CharField(source='register.subject.name', read_only=True)

    class Meta:
        model = StudentMarks
        fields = [
            'id', 'register', 'student', 'student_name',
            'exam_name', 'subject_name',
            'theory_marks', 'practical_marks', 'internal_marks',
            'total_marks', 'grade', 'is_absent',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'exam_name', 'subject_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# EXAM RESULT SERIALIZERS
# ============================================================================


class ExamResultListSerializer(serializers.ModelSerializer):
    """Serializer for listing exam results (minimal fields)."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = ExamResult
        fields = [
            'id', 'student', 'student_name', 'exam', 'exam_name',
            'total_marks', 'marks_obtained', 'percentage',
            'grade', 'result_status', 'rank'
        ]
        read_only_fields = ['id', 'student_name', 'exam_name']


class ExamResultSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for ExamResult model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = ExamResult
        fields = [
            'id', 'student', 'student_name', 'exam', 'exam_name',
            'total_marks', 'marks_obtained', 'percentage',
            'grade', 'result_status', 'rank', 'remarks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'exam_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# PROGRESS CARD SERIALIZERS
# ============================================================================


class ProgressCardSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for ProgressCard model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = ProgressCard
        fields = [
            'id', 'student', 'student_name', 'exam', 'exam_name',
            'card_file', 'issue_date',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'exam_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# MARK SHEET SERIALIZERS
# ============================================================================


class MarkSheetSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for MarkSheet model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = MarkSheet
        fields = [
            'id', 'student', 'student_name', 'exam', 'exam_name',
            'sheet_number', 'sheet_file', 'issue_date',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'exam_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# TABULATION SHEET SERIALIZERS
# ============================================================================


class TabulationSheetSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for TabulationSheet model."""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = TabulationSheet
        fields = [
            'id', 'exam', 'exam_name', 'class_obj', 'class_name',
            'section', 'section_name', 'sheet_file', 'issue_date',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'exam_name', 'class_name', 'section_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
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
