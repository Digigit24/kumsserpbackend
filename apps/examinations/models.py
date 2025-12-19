from django.db import models
from django.conf import settings

from apps.core.models import CollegeScopedModel, AuditModel, College
from apps.academic.models import Class as AcademicClass, Section, Subject, Classroom, AcademicSession
from apps.students.models import Student
from apps.teachers.models import Teacher


class MarksGrade(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='marks_grades')
    name = models.CharField(max_length=50)
    grade = models.CharField(max_length=10)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    remarks = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'marks_grade'
        indexes = [
            models.Index(fields=['college', 'grade']),
        ]

    def __str__(self):
        return f"{self.grade} ({self.min_percentage}-{self.max_percentage})"


class ExamType(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='exam_types')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'exam_type'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Exam(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=200)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='exams')
    class_obj = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='exams')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='exams')
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = 'exam'
        indexes = [
            models.Index(fields=['college', 'exam_type', 'class_obj', 'start_date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.class_obj})"


class ExamSchedule(AuditModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_schedules')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_schedules')
    invigilator = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='invigilated_exams')
    max_marks = models.IntegerField()

    class Meta:
        db_table = 'exam_schedule'
        indexes = [
            models.Index(fields=['exam', 'subject', 'date']),
        ]

    def __str__(self):
        return f"{self.exam} - {self.subject} on {self.date}"


class ExamAttendance(AuditModel):
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attendance')
    status = models.CharField(max_length=20)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'exam_attendance'
        unique_together = ['exam_schedule', 'student']
        indexes = [
            models.Index(fields=['exam_schedule', 'student']),
        ]

    def __str__(self):
        return f"{self.student} - {self.exam_schedule}"


class AdmitCard(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='admit_cards')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='admit_cards')
    card_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    card_file = models.FileField(upload_to='admit_cards/', null=True, blank=True)

    class Meta:
        db_table = 'admit_card'
        unique_together = ['student', 'exam']
        indexes = [
            models.Index(fields=['student', 'exam', 'card_number']),
        ]

    def __str__(self):
        return f"AdmitCard {self.card_number}"


class MarksRegister(AuditModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks_registers')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='marks_registers')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name='marks_registers')
    max_marks = models.IntegerField()
    pass_marks = models.IntegerField()

    class Meta:
        db_table = 'marks_register'
        unique_together = ['exam', 'subject', 'section']
        indexes = [
            models.Index(fields=['exam', 'subject', 'section']),
        ]

    def __str__(self):
        return f"{self.exam} - {self.subject}"


class StudentMarks(AuditModel):
    register = models.ForeignKey(MarksRegister, on_delete=models.CASCADE, related_name='student_marks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_marks')
    theory_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    practical_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    internal_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    grade = models.CharField(max_length=10, null=True, blank=True)
    is_absent = models.BooleanField(default=False)

    class Meta:
        db_table = 'student_marks'
        unique_together = ['register', 'student']
        indexes = [
            models.Index(fields=['register', 'student']),
        ]

    def __str__(self):
        return f"{self.student} - {self.register}"


class ExamResult(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    total_marks = models.DecimalField(max_digits=8, decimal_places=2)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=10, null=True, blank=True)
    result_status = models.CharField(max_length=20)
    rank = models.IntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'exam_result'
        unique_together = ['student', 'exam']
        indexes = [
            models.Index(fields=['student', 'exam', 'percentage']),
        ]

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.result_status}"


class ProgressCard(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_cards')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='progress_cards')
    card_file = models.FileField(upload_to='progress_cards/', null=True, blank=True)
    issue_date = models.DateField()

    class Meta:
        db_table = 'progress_card'
        unique_together = ['student', 'exam']
        indexes = [
            models.Index(fields=['student', 'exam']),
        ]

    def __str__(self):
        return f"ProgressCard {self.student} - {self.exam}"


class MarkSheet(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mark_sheets')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='mark_sheets')
    sheet_number = models.CharField(max_length=50, unique=True)
    sheet_file = models.FileField(upload_to='mark_sheets/', null=True, blank=True)
    issue_date = models.DateField()

    class Meta:
        db_table = 'mark_sheet'
        indexes = [
            models.Index(fields=['student', 'exam', 'sheet_number']),
        ]

    def __str__(self):
        return f"MarkSheet {self.sheet_number}"


class TabulationSheet(AuditModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='tabulation_sheets')
    class_obj = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='tabulation_sheets')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name='tabulation_sheets')
    sheet_file = models.FileField(upload_to='tabulation_sheets/', null=True, blank=True)
    issue_date = models.DateField()

    class Meta:
        db_table = 'tabulation_sheet'
        indexes = [
            models.Index(fields=['exam', 'class_obj', 'section']),
        ]

    def __str__(self):
        return f"Tabulation - {self.exam} - {self.class_obj}"
