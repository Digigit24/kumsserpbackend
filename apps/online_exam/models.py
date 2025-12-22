from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.core.models import CollegeScopedModel, AuditModel, College
from apps.academic.models import Subject, Class as AcademicClass, Section
from apps.students.models import Student


class QuestionBank(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='question_banks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='question_banks')
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'question_bank'
        indexes = [
            models.Index(fields=['college', 'subject']),
        ]

    def __str__(self):
        return self.name


class Question(AuditModel):
    bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20)
    question_text = models.TextField()
    question_image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    correct_answer = models.TextField(null=True, blank=True)
    difficulty_level = models.CharField(max_length=20, null=True, blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    explanation = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'question'
        indexes = [
            models.Index(fields=['bank', 'question_type', 'difficulty_level']),
        ]

    def __str__(self):
        return self.question_text[:50]


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.TextField()
    option_image = models.ImageField(upload_to='question_options/', null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'question_option'
        indexes = [
            models.Index(fields=['question']),
        ]

    def __str__(self):
        return self.option_text[:50]


class OnlineExam(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='online_exams')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='online_exams')
    class_obj = models.ForeignKey(AcademicClass, on_delete=models.CASCADE, related_name='online_exams')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True, related_name='online_exams')
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    duration = models.IntegerField()
    total_marks = models.IntegerField()
    pass_marks = models.IntegerField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    negative_marking = models.BooleanField(default=False)
    negative_marks = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    allow_review = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = 'online_exam'
        indexes = [
            models.Index(fields=['college', 'subject', 'class_obj', 'start_datetime']),
        ]

    def __str__(self):
        return self.name


class ExamQuestion(AuditModel):
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='exam_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='exam_questions')
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'exam_question'
        unique_together = ['exam', 'question']
        indexes = [
            models.Index(fields=['exam', 'question', 'order']),
        ]

    def __str__(self):
        return f"{self.exam} - Q{self.question_id}"


class StudentExamAttempt(AuditModel):
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attempts')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    submission_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tab_switch_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'student_exam_attempt'
        unique_together = ['exam', 'student']
        indexes = [
            models.Index(fields=['exam', 'student', 'start_time']),
        ]

    def __str__(self):
        return f"{self.student} - {self.exam}"


class StudentAnswer(AuditModel):
    attempt = models.ForeignKey(StudentExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='selected_answers')
    answer_text = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    time_taken = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'student_answer'
        unique_together = ['attempt', 'question']
        indexes = [
            models.Index(fields=['attempt', 'question']),
        ]

    def __str__(self):
        return f"{self.attempt} - Q{self.question_id}"
