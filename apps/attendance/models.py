"""
Attendance models for the KUMSS ERP system.
Provides student and staff attendance tracking.
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.core.managers import CollegeManager
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.academic.models import Class, Section, SubjectAssignment, ClassTime


class StudentAttendance(TimeStampedModel):
    """
    Tracks daily attendance for students.
    """
    objects = CollegeManager()

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='daily_attendance',
        help_text="Student reference"
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='student_attendance',
        help_text="Class reference"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='student_attendance',
        help_text="Section reference"
    )
    date = models.DateField(help_text="Attendance date")
    status = models.CharField(
        max_length=20,
        help_text="Status (present/absent/late/half_day)"
    )
    check_in_time = models.TimeField(null=True, blank=True, help_text="Check-in time")
    check_out_time = models.TimeField(null=True, blank=True, help_text="Check-out time")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_student_attendance',
        help_text="Marked by"
    )

    class Meta:
        db_table = 'student_attendance'
        verbose_name = 'Student Attendance'
        verbose_name_plural = 'Student Attendance'
        unique_together = ['student', 'date']
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['date', 'class_obj', 'section']),
            models.Index(fields=['class_obj', 'section']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"


class SubjectAttendance(TimeStampedModel):
    """
    Tracks subject-wise attendance for students.
    """
    objects = CollegeManager()

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='subject_attendance',
        help_text="Student reference"
    )
    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="Subject assignment"
    )
    date = models.DateField(help_text="Attendance date")
    period = models.ForeignKey(
        ClassTime,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subject_attendance',
        help_text="Class period"
    )
    status = models.CharField(
        max_length=20,
        help_text="Status (present/absent/late)"
    )
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")
    marked_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_subject_attendance',
        help_text="Marked by"
    )

    class Meta:
        db_table = 'subject_attendance'
        verbose_name = 'Subject Attendance'
        verbose_name_plural = 'Subject Attendance'
        unique_together = ['student', 'subject_assignment', 'date', 'period']
        indexes = [
            models.Index(fields=['student', 'subject_assignment', 'date']),
            models.Index(fields=['date', 'period']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject_assignment.subject.short_name} - {self.date}"


class StaffAttendance(TimeStampedModel):
    """
    Tracks daily attendance for staff/teachers.
    """
    objects = CollegeManager()

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='attendance',
        help_text="Teacher reference"
    )
    date = models.DateField(help_text="Attendance date")
    status = models.CharField(
        max_length=20,
        help_text="Status (present/absent/on_leave/half_day)"
    )
    check_in_time = models.TimeField(null=True, blank=True, help_text="Check-in time")
    check_out_time = models.TimeField(null=True, blank=True, help_text="Check-out time")
    # Leave application reference - will be added when leave app is created
    # leave = models.ForeignKey(
    #     'leave.LeaveApplication',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='staff_attendance',
    #     help_text="Leave reference"
    # )
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_staff_attendance',
        help_text="Marked by"
    )

    class Meta:
        db_table = 'staff_attendance'
        verbose_name = 'Staff Attendance'
        verbose_name_plural = 'Staff Attendance'
        unique_together = ['teacher', 'date']
        indexes = [
            models.Index(fields=['teacher', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.date} - {self.status}"


class AttendanceNotification(TimeStampedModel):
    """
    Manages notifications for attendance (to parents, students, etc.).
    """
    objects = CollegeManager()

    attendance = models.ForeignKey(
        StudentAttendance,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="Attendance reference"
    )
    recipient_type = models.CharField(
        max_length=20,
        help_text="Recipient type (parent/student/admin)"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_notifications',
        help_text="Recipient"
    )
    notification_type = models.CharField(
        max_length=20,
        help_text="Notification type (sms/email/whatsapp/push)"
    )
    status = models.CharField(
        max_length=20,
        default='pending',
        help_text="Status (pending/sent/delivered/failed)"
    )
    sent_at = models.DateTimeField(null=True, blank=True, help_text="Sent timestamp")
    delivered_at = models.DateTimeField(null=True, blank=True, help_text="Delivered timestamp")
    error_message = models.TextField(null=True, blank=True, help_text="Error message")
    message = models.TextField(help_text="Message content")

    class Meta:
        db_table = 'attendance_notification'
        verbose_name = 'Attendance Notification'
        verbose_name_plural = 'Attendance Notifications'
        indexes = [
            models.Index(fields=['attendance', 'recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"Notification for {self.attendance.student.get_full_name()} - {self.notification_type}"
