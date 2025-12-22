"""
Signals for Online Exam app.
Currently placeholders; extend with notification/evaluation logic as needed.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.online_exam.models import OnlineExam, StudentExamAttempt, StudentAnswer


@receiver(post_save, sender=OnlineExam)
def online_exam_post_save(sender, instance, created, **kwargs):
    # TODO: if instance.is_published, notify students and create attempts
    return


@receiver(post_save, sender=StudentExamAttempt)
def student_exam_attempt_post_save(sender, instance, created, **kwargs):
    # TODO: on completion, auto-evaluate objective answers and update marks
    return


@receiver(post_save, sender=StudentAnswer)
def student_answer_post_save(sender, instance, created, **kwargs):
    # TODO: auto-check MCQ/TF and assign marks/negative marks
    return
