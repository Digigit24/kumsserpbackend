from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import CollegeScopedModel, AuditModel, College, AcademicSession


class Faculty(CollegeScopedModel):
    """
    Represents a faculty or department within a college.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='faculties',
        help_text="College reference"
    )
    code = models.CharField(max_length=20, help_text="Faculty code")
    name = models.CharField(max_length=200, help_text="Faculty name")
    short_name = models.CharField(max_length=50, help_text="Short name")
    description = models.TextField(null=True, blank=True, help_text="Description")
    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_faculties',
        help_text="Head of Department"
    )
    display_order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        db_table = 'faculty'
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'
        ordering = ['display_order', 'name']
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Program(CollegeScopedModel):
    """
    Represents an academic program (e.g., B.Tech, M.Sc).
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='programs',
        help_text="College reference"
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='programs',
        help_text="Faculty reference"
    )
    code = models.CharField(max_length=20, help_text="Program code")
    name = models.CharField(max_length=200, help_text="Program name")
    short_name = models.CharField(max_length=50, help_text="Short name")
    program_type = models.CharField(max_length=20, help_text="Type (ug/pg/diploma)")
    duration = models.IntegerField(help_text="Duration")
    duration_type = models.CharField(max_length=20, help_text="Type (semester/year)")
    total_credits = models.IntegerField(null=True, blank=True, help_text="Total credits")
    description = models.TextField(null=True, blank=True, help_text="Description")
    display_order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        db_table = 'program'
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
        ordering = ['display_order', 'name']
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'faculty', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Class(CollegeScopedModel):
    """
    Represents a specific class (e.g., CS-A, Semester 1).
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='classes',
        help_text="College reference"
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='classes',
        help_text="Program reference"
    )
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='classes',
        help_text="Session reference"
    )
    name = models.CharField(max_length=100, help_text="Class name")
    semester = models.IntegerField(help_text="Semester number")
    year = models.IntegerField(help_text="Year number")
    max_students = models.IntegerField(default=60, help_text="Max students")

    class Meta:
        db_table = 'class'
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        unique_together = ['college', 'program', 'academic_session', 'semester']
        indexes = [
            models.Index(fields=['college', 'program', 'academic_session']),
        ]

    def __str__(self):
        return f"{self.name} - {self.program.short_name}"


class Section(AuditModel):
    """
    Represents a section within a class (e.g., Section A).
    """
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='sections',
        help_text="Class reference"
    )
    name = models.CharField(max_length=10, help_text="Section name")
    max_students = models.IntegerField(default=60, help_text="Max students")

    class Meta:
        db_table = 'section'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        unique_together = ['class_obj', 'name']
        indexes = [
            models.Index(fields=['class_obj']),
        ]

    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"


class Subject(CollegeScopedModel):
    """
    Represents a subject/course.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="College reference"
    )
    code = models.CharField(max_length=20, help_text="Subject code")
    name = models.CharField(max_length=200, help_text="Subject name")
    short_name = models.CharField(max_length=50, help_text="Short name")
    subject_type = models.CharField(max_length=20, help_text="Type (theory/practical)")
    credits = models.DecimalField(max_digits=4, decimal_places=2, help_text="Credits")
    theory_hours = models.IntegerField(default=0, help_text="Theory hours/week")
    practical_hours = models.IntegerField(default=0, help_text="Practical hours/week")
    max_marks = models.IntegerField(help_text="Maximum marks")
    pass_marks = models.IntegerField(help_text="Passing marks")
    description = models.TextField(null=True, blank=True, help_text="Description")

    class Meta:
        db_table = 'subject'
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class OptionalSubject(AuditModel):
    """
    Represents a group of optional subjects.
    """
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='optional_subjects',
        help_text="Class reference"
    )
    name = models.CharField(max_length=100, help_text="Group name")
    description = models.TextField(null=True, blank=True, help_text="Description")
    subjects = models.ManyToManyField(Subject, related_name='optional_groups', help_text="Subject list")
    min_selection = models.IntegerField(default=1, help_text="Min selection")
    max_selection = models.IntegerField(default=1, help_text="Max selection")

    class Meta:
        db_table = 'optional_subject'
        verbose_name = 'Optional Subject Group'
        verbose_name_plural = 'Optional Subject Groups'
        indexes = [
            models.Index(fields=['class_obj']),
        ]

    def __str__(self):
        return f"{self.name} ({self.class_obj.name})"


class SubjectAssignment(AuditModel):
    """
    Assigns a subject to a class/section and teacher.
    """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_assignments',
        help_text="Subject reference"
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='subject_assignments',
        help_text="Class reference"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subject_assignments',
        help_text="Section reference"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subject_assignments',
        help_text="Teacher reference"
    )
    lab_instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_assignments',
        help_text="Lab instructor"
    )
    is_optional = models.BooleanField(default=False, help_text="Optional flag")

    class Meta:
        db_table = 'subject_assignment'
        verbose_name = 'Subject Assignment'
        verbose_name_plural = 'Subject Assignments'
        unique_together = ['subject', 'class_obj', 'section']
        indexes = [
            models.Index(fields=['subject', 'class_obj', 'section', 'teacher']),
        ]

    def __str__(self):
        return f"{self.subject.short_name} - {self.class_obj.name}"


class Classroom(CollegeScopedModel):
    """
    Represents a physical classroom or lab.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='classrooms',
        help_text="College reference"
    )
    code = models.CharField(max_length=20, help_text="Room code")
    name = models.CharField(max_length=100, help_text="Room name")
    room_type = models.CharField(max_length=20, help_text="Type (classroom/lab)")
    building = models.CharField(max_length=100, null=True, blank=True, help_text="Building name")
    floor = models.CharField(max_length=20, null=True, blank=True, help_text="Floor number")
    capacity = models.IntegerField(help_text="Seating capacity")
    has_projector = models.BooleanField(default=False, help_text="Has projector")
    has_ac = models.BooleanField(default=False, help_text="Has AC")
    has_computer = models.BooleanField(default=False, help_text="Has computer")

    class Meta:
        db_table = 'classroom'
        verbose_name = 'Classroom'
        verbose_name_plural = 'Classrooms'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassTime(CollegeScopedModel):
    """
    Defines time slots/periods for classes.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='class_times',
        help_text="College reference"
    )
    period_number = models.IntegerField(help_text="Period number")
    start_time = models.TimeField(help_text="Start time")
    end_time = models.TimeField(help_text="End time")
    is_break = models.BooleanField(default=False, help_text="Break flag")
    break_name = models.CharField(max_length=50, null=True, blank=True, help_text="Break name")

    class Meta:
        db_table = 'class_time'
        verbose_name = 'Class Time'
        verbose_name_plural = 'Class Times'
        unique_together = ['college', 'period_number']
        indexes = [
            models.Index(fields=['college', 'period_number']),
        ]

    def __str__(self):
        return f"Period {self.period_number} ({self.start_time} - {self.end_time})"


class Timetable(AuditModel):
    """
    Represents the weekly timetable.
    """
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        help_text="Class reference"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        help_text="Section reference"
    )
    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        help_text="Subject assignment"
    )
    day_of_week = models.IntegerField(help_text="Day (0-6)")
    class_time = models.ForeignKey(
        ClassTime,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        help_text="Class time"
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetable_entries',
        help_text="Classroom"
    )
    effective_from = models.DateField(help_text="Effective from")
    effective_to = models.DateField(null=True, blank=True, help_text="Effective to")

    class Meta:
        db_table = 'timetable'
        verbose_name = 'Timetable'
        verbose_name_plural = 'Timetables'
        unique_together = ['section', 'day_of_week', 'class_time', 'effective_from']
        indexes = [
            models.Index(fields=['section', 'day_of_week', 'class_time', 'effective_from']),
        ]

    def __str__(self):
        return f"{self.section} - {self.day_of_week} - {self.class_time}"


class LabSchedule(AuditModel):
    """
    Represents lab schedules.
    """
    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='lab_schedules',
        help_text="Subject assignment"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='lab_schedules',
        help_text="Section reference"
    )
    day_of_week = models.IntegerField(help_text="Day (0-6)")
    start_time = models.TimeField(help_text="Start time")
    end_time = models.TimeField(help_text="End time")
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_schedules',
        help_text="Lab room"
    )
    batch_name = models.CharField(max_length=50, null=True, blank=True, help_text="Batch name")
    effective_from = models.DateField(help_text="Effective from")
    effective_to = models.DateField(null=True, blank=True, help_text="Effective to")

    class Meta:
        db_table = 'lab_schedule'
        verbose_name = 'Lab Schedule'
        verbose_name_plural = 'Lab Schedules'
        indexes = [
            models.Index(fields=['subject_assignment', 'section']),
        ]

    def __str__(self):
        return f"{self.section} - Lab - {self.day_of_week}"


class ClassTeacher(AuditModel):
    """
    Assigns a class teacher to a class/section.
    """
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='class_teachers',
        help_text="Class reference"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='class_teachers',
        help_text="Section reference"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='class_teacher_assignments',
        help_text="Teacher reference"
    )
    assigned_from = models.DateField(help_text="Assigned from")
    assigned_to = models.DateField(null=True, blank=True, help_text="Assigned to")
    is_current = models.BooleanField(default=True, help_text="Current flag")

    class Meta:
        db_table = 'class_teacher'
        verbose_name = 'Class Teacher'
        verbose_name_plural = 'Class Teachers'
        indexes = [
            models.Index(fields=['class_obj', 'section', 'teacher']),
        ]

    def __str__(self):
        return f"{self.teacher} - {self.section}"
