"""
Teacher models for the KUMSS ERP system.
Provides teacher information, study materials, assignments, and homework management.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import CollegeScopedModel, AuditModel, TimeStampedModel, College
from apps.academic.models import Faculty, Subject, Class, Section
from apps.students.models import Student


class Teacher(CollegeScopedModel):
    """
    Represents a teacher in the system.
    Qualifications and experience are stored as JSON arrays.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        help_text="User account"
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='teachers',
        help_text="College reference"
    )
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Employee ID"
    )
    joining_date = models.DateField(help_text="Joining date")
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers',
        help_text="Faculty/Department"
    )

    # Personal details
    first_name = models.CharField(max_length=100, help_text="First name")
    middle_name = models.CharField(max_length=100, null=True, blank=True, help_text="Middle name")
    last_name = models.CharField(max_length=100, help_text="Last name")
    date_of_birth = models.DateField(help_text="Date of birth")
    gender = models.CharField(max_length=10, help_text="Gender")
    email = models.EmailField(help_text="Email")
    phone = models.CharField(max_length=20, help_text="Phone")
    alternate_phone = models.CharField(max_length=20, null=True, blank=True, help_text="Alternate phone")
    address = models.TextField(null=True, blank=True, help_text="Address")
    photo = models.ImageField(upload_to='teacher_photos/', null=True, blank=True, help_text="Photo")

    # Professional details
    specialization = models.CharField(max_length=200, null=True, blank=True, help_text="Main specialization")
    
    # JSON fields for flexible data
    qualifications = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="List of degrees (Name, Year, University)"
    )
    experience_details = models.JSONField(
        default=list,
        null=True,
        blank=True,
        help_text="List of past jobs (Organization, Role, Dates)"
    )
    custom_attributes = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="Custom key-value pairs"
    )

    # Status
    resignation_date = models.DateField(null=True, blank=True, help_text="Resignation date")

    class Meta:
        db_table = 'teacher'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        unique_together = ['college', 'employee_id']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['college']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"

    def get_full_name(self):
        """Return the full name of the teacher."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class StudyMaterial(CollegeScopedModel):
    """
    Represents study materials uploaded by teachers.
    """
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='study_materials',
        help_text="Teacher reference"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='study_materials',
        help_text="Subject reference"
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='study_materials',
        help_text="Class reference"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_materials',
        help_text="Section reference"
    )
    title = models.CharField(max_length=300, help_text="Material title")
    description = models.TextField(null=True, blank=True, help_text="Description")
    content_type = models.CharField(
        max_length=20,
        help_text="Content type (pdf/video/document/link)"
    )
    file = models.FileField(upload_to='study_materials/', null=True, blank=True, help_text="File upload")
    external_url = models.URLField(null=True, blank=True, help_text="External URL")
    topic = models.CharField(max_length=200, null=True, blank=True, help_text="Topic")
    tags = models.CharField(max_length=500, null=True, blank=True, help_text="Tags (comma-separated)")
    upload_date = models.DateField(auto_now_add=True, help_text="Upload date")
    view_count = models.IntegerField(default=0, help_text="View count")

    class Meta:
        db_table = 'study_material'
        verbose_name = 'Study Material'
        verbose_name_plural = 'Study Materials'
        indexes = [
            models.Index(fields=['teacher', 'subject', 'class_obj', 'upload_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.subject.short_name}"


class Assignment(CollegeScopedModel):
    """
    Represents assignments given by teachers.
    """
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text="Teacher reference"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
        help_text="Subject reference"
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='assignments',
        help_text="Class reference"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments',
        help_text="Section reference"
    )
    title = models.CharField(max_length=300, help_text="Assignment title")
    description = models.TextField(help_text="Description")
    assignment_file = models.FileField(
        upload_to='assignments/',
        null=True,
        blank=True,
        help_text="Assignment file"
    )
    assigned_date = models.DateField(auto_now_add=True, help_text="Assigned date")
    due_date = models.DateField(help_text="Due date")
    max_marks = models.IntegerField(help_text="Maximum marks")
    allow_late_submission = models.BooleanField(default=False, help_text="Allow late submission")
    late_submission_penalty = models.IntegerField(default=0, help_text="Penalty percentage")

    class Meta:
        db_table = 'assignment'
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        indexes = [
            models.Index(fields=['teacher', 'subject', 'class_obj', 'due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.subject.short_name}"


class AssignmentSubmission(TimeStampedModel):
    """
    Tracks student submissions for assignments.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Assignment reference"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        help_text="Student reference"
    )
    submission_date = models.DateTimeField(auto_now_add=True, help_text="Submission date")
    submission_file = models.FileField(
        upload_to='assignment_submissions/',
        null=True,
        blank=True,
        help_text="Submission file"
    )
    submission_text = models.TextField(null=True, blank=True, help_text="Submission text")
    status = models.CharField(
        max_length=20,
        default='submitted',
        help_text="Status (pending/submitted/graded)"
    )
    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Marks obtained"
    )
    feedback = models.TextField(null=True, blank=True, help_text="Feedback")
    graded_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        help_text="Graded by"
    )
    graded_date = models.DateTimeField(null=True, blank=True, help_text="Graded date")
    is_late = models.BooleanField(default=False, help_text="Late submission flag")

    class Meta:
        db_table = 'assignment_submission'
        verbose_name = 'Assignment Submission'
        verbose_name_plural = 'Assignment Submissions'
        unique_together = ['assignment', 'student']
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.assignment.title} - {self.student.get_full_name()}"


class Homework(CollegeScopedModel):
    """
    Represents homework assigned by teachers.
    """
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='homework',
        help_text="Teacher reference"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='homework',
        help_text="Subject reference"
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='homework',
        help_text="Class reference"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='homework',
        help_text="Section reference"
    )
    title = models.CharField(max_length=300, help_text="Homework title")
    description = models.TextField(help_text="Description")
    attachment = models.FileField(
        upload_to='homework/',
        null=True,
        blank=True,
        help_text="Attachment"
    )
    assigned_date = models.DateField(auto_now_add=True, help_text="Assigned date")
    due_date = models.DateField(help_text="Due date")

    class Meta:
        db_table = 'homework'
        verbose_name = 'Homework'
        verbose_name_plural = 'Homework'
        indexes = [
            models.Index(fields=['teacher', 'subject', 'class_obj', 'due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.subject.short_name}"


class HomeworkSubmission(TimeStampedModel):
    """
    Tracks student homework submissions.
    """
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Homework reference"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='homework_submissions',
        help_text="Student reference"
    )
    status = models.CharField(
        max_length=20,
        default='pending',
        help_text="Status (pending/completed/checked)"
    )
    completion_date = models.DateField(null=True, blank=True, help_text="Completion date")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")
    checked_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checked_homework',
        help_text="Checked by"
    )
    checked_date = models.DateField(null=True, blank=True, help_text="Checked date")

    class Meta:
        db_table = 'homework_submission'
        verbose_name = 'Homework Submission'
        verbose_name_plural = 'Homework Submissions'
        unique_together = ['homework', 'student']
        indexes = [
            models.Index(fields=['homework', 'student']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.homework.title} - {self.student.get_full_name()}"
