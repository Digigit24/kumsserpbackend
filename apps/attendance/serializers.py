"""
DRF Serializers for Attendance app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    StudentAttendance, SubjectAttendance, StaffAttendance, AttendanceNotification
)
from apps.core.serializers import UserBasicSerializer

User = get_user_model()


# ============================================================================
# STUDENT ATTENDANCE SERIALIZERS
# ============================================================================


class StudentAttendanceListSerializer(serializers.ModelSerializer):
    """Serializer for listing student attendance (minimal fields)."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'student', 'student_name', 'class_obj', 'class_name',
            'section', 'section_name', 'date', 'status', 'check_in_time', 'check_out_time'
        ]
        read_only_fields = ['id', 'student_name', 'class_name', 'section_name']


class StudentAttendanceSerializer(serializers.ModelSerializer):
    """Full serializer for StudentAttendance model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    marked_by_details = UserBasicSerializer(source='marked_by', read_only=True)

    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'student', 'student_name', 'class_obj', 'class_name',
            'section', 'section_name', 'date', 'status',
            'check_in_time', 'check_out_time', 'remarks',
            'marked_by', 'marked_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'class_name', 'section_name', 'marked_by_details', 'created_at', 'updated_at']


# ============================================================================
# SUBJECT ATTENDANCE SERIALIZERS
# ============================================================================


class SubjectAttendanceListSerializer(serializers.ModelSerializer):
    """Serializer for listing subject attendance (minimal fields)."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject_assignment.subject.short_name', read_only=True)
    period_time = serializers.CharField(source='period.__str__', read_only=True)

    class Meta:
        model = SubjectAttendance
        fields = [
            'id', 'student', 'student_name', 'subject_assignment', 'subject_name',
            'date', 'period', 'period_time', 'status'
        ]
        read_only_fields = ['id', 'student_name', 'subject_name', 'period_time']


class SubjectAttendanceSerializer(serializers.ModelSerializer):
    """Full serializer for SubjectAttendance model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject_assignment.subject.name', read_only=True)
    class_name = serializers.CharField(source='subject_assignment.class_obj.name', read_only=True)
    period_details = serializers.CharField(source='period.__str__', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_full_name', read_only=True)

    class Meta:
        model = SubjectAttendance
        fields = [
            'id', 'student', 'student_name', 'subject_assignment', 'subject_name', 'class_name',
            'date', 'period', 'period_details', 'status', 'remarks',
            'marked_by', 'marked_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'subject_name', 'class_name', 'period_details', 'marked_by_name', 'created_at', 'updated_at']


# ============================================================================
# STAFF ATTENDANCE SERIALIZERS
# ============================================================================


class StaffAttendanceListSerializer(serializers.ModelSerializer):
    """Serializer for listing staff attendance (minimal fields)."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = StaffAttendance
        fields = [
            'id', 'teacher', 'teacher_name', 'date', 'status',
            'check_in_time', 'check_out_time'
        ]
        read_only_fields = ['id', 'teacher_name']


class StaffAttendanceSerializer(serializers.ModelSerializer):
    """Full serializer for StaffAttendance model."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    marked_by_details = UserBasicSerializer(source='marked_by', read_only=True)

    class Meta:
        model = StaffAttendance
        fields = [
            'id', 'teacher', 'teacher_name', 'date', 'status',
            'check_in_time', 'check_out_time', 'remarks',
            'marked_by', 'marked_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher_name', 'marked_by_details', 'created_at', 'updated_at']


# ============================================================================
# ATTENDANCE NOTIFICATION SERIALIZERS
# ============================================================================


class AttendanceNotificationSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceNotification model."""
    student_name = serializers.CharField(source='attendance.student.get_full_name', read_only=True)
    recipient_details = UserBasicSerializer(source='recipient', read_only=True)

    class Meta:
        model = AttendanceNotification
        fields = [
            'id', 'attendance', 'student_name', 'recipient_type', 'recipient', 'recipient_details',
            'notification_type', 'status', 'message',
            'sent_at', 'delivered_at', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'recipient_details', 'created_at', 'updated_at']


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


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance marking."""
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of student IDs"
    )
    date = serializers.DateField(help_text="Attendance date")
    status = serializers.CharField(max_length=20, help_text="Attendance status")
    class_obj = serializers.IntegerField(help_text="Class ID")
    section = serializers.IntegerField(help_text="Section ID")
    remarks = serializers.CharField(required=False, allow_blank=True, help_text="Remarks")
