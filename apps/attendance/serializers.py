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

    subjects = serializers.SerializerMethodField()

    class Meta:
        model = StudentAttendance
        fields = [
            'id', 'student', 'student_name', 'class_obj', 'class_name',
            'section', 'section_name', 'date', 'status', 'check_in_time', 'check_out_time',
            'subjects'
        ]
        read_only_fields = ['id', 'student_name', 'class_name', 'section_name', 'subjects']

    def get_subjects(self, obj):
        """
        Return list of subjects for the student.
        Combined logic:
        1. Subjects assigned to student's class/section (mandatory).
        2. Optional subjects chosen by the student.
        """
        student = obj.student
        class_obj = obj.class_obj
        section = obj.section
        
        # 1. Get mandatory subjects (SubjectAssignments for class/section where is_optional=False)
        from apps.academic.models import SubjectAssignment
        mandatory_assignments = SubjectAssignment.objects.filter(
            class_obj=class_obj,
            section=section,
            is_optional=False
        ).select_related('subject')

        subjects_data = []
        seen_subject_ids = set()

        for assignment in mandatory_assignments:
            if assignment.subject.id not in seen_subject_ids:
                subjects_data.append({
                    'id': assignment.subject.id,
                    'name': assignment.subject.name,
                    'code': assignment.subject.code,
                    'is_optional': False
                })
                seen_subject_ids.add(assignment.subject.id)
        
        # 2. Add student's specifically chosen optional subjects
        # Note: We look at student.optional_subjects which is M2M to Subject
        for subject in student.optional_subjects.all():
             if subject.id not in seen_subject_ids:
                 subjects_data.append({
                     'id': subject.id,
                     'name': subject.name,
                     'code': subject.code,
                     'is_optional': True
                 })
                 seen_subject_ids.add(subject.id)

        return subjects_data


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
    subject_name = serializers.CharField(source='subject_assignment.subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject_assignment.subject.code', read_only=True)
    class_name = serializers.CharField(source='subject_assignment.class_obj.name', read_only=True)
    section_name = serializers.CharField(source='subject_assignment.section.name', read_only=True)
    period_time = serializers.CharField(source='period.__str__', read_only=True)

    class Meta:
        model = SubjectAttendance
        fields = [
            'id', 'student', 'student_name', 'subject_assignment', 'subject_name', 'subject_code',
            'class_name', 'section_name',
            'date', 'period', 'period_time', 'status'
        ]
        read_only_fields = ['id', 'student_name', 'subject_name', 'subject_code', 'class_name', 'section_name', 'period_time']


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
    remarks = serializers.CharField(required=False, allow_null=True, allow_blank=True, help_text="Remarks")


class StudentWithAttendanceSerializer(serializers.Serializer):
    """Serializer for student with their daily attendance status."""
    student_id = serializers.IntegerField(read_only=True)
    admission_number = serializers.CharField(read_only=True)
    roll_number = serializers.CharField(read_only=True)
    student_name = serializers.CharField(read_only=True)
    attendance_id = serializers.IntegerField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True, allow_null=True)
    check_in_time = serializers.TimeField(read_only=True, allow_null=True)
    check_out_time = serializers.TimeField(read_only=True, allow_null=True)
    remarks = serializers.CharField(read_only=True, allow_null=True)
    marked_by = serializers.IntegerField(read_only=True, allow_null=True)
    marked_by_name = serializers.CharField(read_only=True, allow_null=True)


class StudentWithSubjectAttendanceSerializer(serializers.Serializer):
    """Serializer for student with their subject attendance status."""
    student_id = serializers.IntegerField(read_only=True)
    admission_number = serializers.CharField(read_only=True)
    roll_number = serializers.CharField(read_only=True)
    student_name = serializers.CharField(read_only=True)
    attendance_id = serializers.IntegerField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True, allow_null=True)
    remarks = serializers.CharField(read_only=True, allow_null=True)
    marked_by = serializers.IntegerField(read_only=True, allow_null=True)
    marked_by_name = serializers.CharField(read_only=True, allow_null=True)
