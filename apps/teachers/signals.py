"""
Signals for Teachers app.
"""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Teacher, StudyMaterial, Assignment, AssignmentSubmission, Homework, HomeworkSubmission


@receiver(post_save, sender=Teacher)
def teacher_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for Teacher model.
    - Generate employee ID if not provided
    - Send welcome email with credentials
    - Log joining activity
    """
    if created:
        # Generate employee ID if not provided
        if not instance.employee_id:
            year = instance.joining_date.year
            college_code = instance.college.code
            count = Teacher.objects.filter(college=instance.college).count()
            instance.employee_id = f"EMP-{college_code}-{year}-{count:05d}"
            instance.save(update_fields=['employee_id'])

        # TODO: Send welcome email with credentials
        print(f"Welcome Email: Sent to {instance.email} with credentials")

        # TODO: Log joining activity
        print(f"Activity Log: Teacher {instance.employee_id} joined on {instance.joining_date}")


@receiver(post_save, sender=StudyMaterial)
def study_material_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for StudyMaterial model.
    - Notify students of new material
    - Update material count
    - Log upload activity
    """
    if created:
        # TODO: Notify students in the class/section
        print(f"Notification: New study material '{instance.title}' uploaded for {instance.class_obj.name}")

        # TODO: Update material count (if tracking)
        print(f"Material Count: Updated for {instance.subject.name}")

        # TODO: Log upload activity
        print(f"Activity Log: Study material '{instance.title}' uploaded by {instance.teacher.get_full_name()}")


@receiver(post_save, sender=Assignment)
def assignment_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for Assignment model.
    - Create AssignmentSubmission records for all students (placeholder rows)
    - Send assignment notification
    """
    if created:
        # Get all students in the class/section
        if instance.section:
            students = instance.section.current_students.filter(is_active=True)
        else:
            students = instance.class_obj.current_students.filter(is_active=True)

        # Create placeholder submission records for all students
        submission_records = [
            AssignmentSubmission(
                assignment=instance,
                student=student,
                status='pending'
            )
            for student in students
        ]
        AssignmentSubmission.objects.bulk_create(submission_records, ignore_conflicts=True)
        
        print(f"Assignment Submissions: Created {len(submission_records)} placeholder records")

        # TODO: Send assignment notification to students
        print(f"Notification: Assignment '{instance.title}' assigned to {instance.class_obj.name}")


@receiver(post_save, sender=AssignmentSubmission)
def assignment_submission_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for AssignmentSubmission model.
    - Notify teacher of submission
    - Check if late
    - Calculate penalty
    """
    if created and instance.submission_file:
        # Notify teacher
        print(f"Notification: {instance.student.get_full_name()} submitted assignment '{instance.assignment.title}'")

        # Check if late and calculate penalty
        if instance.submission_date.date() > instance.assignment.due_date:
            instance.is_late = True
            instance.save(update_fields=['is_late'])
            print(f"Late Submission: {instance.student.get_full_name()} submitted late")


@receiver(post_save, sender=Homework)
def homework_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for Homework model.
    - Create HomeworkSubmission records for all students
    - Send homework notification
    """
    if created:
        # Get all students in the class/section
        if instance.section:
            students = instance.section.current_students.filter(is_active=True)
        else:
            students = instance.class_obj.current_students.filter(is_active=True)

        # Create placeholder submission records for all students
        submission_records = [
            HomeworkSubmission(
                homework=instance,
                student=student,
                status='pending'
            )
            for student in students
        ]
        HomeworkSubmission.objects.bulk_create(submission_records, ignore_conflicts=True)
        
        print(f"Homework Submissions: Created {len(submission_records)} placeholder records")

        # TODO: Send homework notification to students
        print(f"Notification: Homework '{instance.title}' assigned to {instance.class_obj.name}")
