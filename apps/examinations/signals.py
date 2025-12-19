"""
Signals for Examinations app.
Lightweight placeholders to avoid heavy side effects; expand with real logic as needed.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.examinations.models import Exam, StudentMarks, ExamResult


@receiver(post_save, sender=Exam)
def exam_post_save(sender, instance, created, **kwargs):
    # TODO: create marks registers, admit cards, notifications
    return


@receiver(post_save, sender=StudentMarks)
def student_marks_post_save(sender, instance, created, **kwargs):
    # TODO: calculate grade, update ExamResult
    return


@receiver(post_save, sender=ExamResult)
def exam_result_post_save(sender, instance, created, **kwargs):
    # TODO: generate progress cards, mark sheets, notifications
    return
