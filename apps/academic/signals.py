from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Timetable, SubjectAssignment

@receiver(pre_save, sender=Timetable)
def validate_timetable(sender, instance, **kwargs):
    """
    Validate classroom availability and teacher availability before saving timetable.
    """
    # 1. Validate Classroom Availability
    if instance.classroom:
        conflicts = Timetable.objects.filter(
            classroom=instance.classroom,
            day_of_week=instance.day_of_week,
            class_time=instance.class_time,
            effective_from__lte=instance.effective_from
        ).exclude(pk=instance.pk)
        
        # Check for date overlap
        if instance.effective_to:
            conflicts = conflicts.filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=instance.effective_from)
            )
        
        if conflicts.exists():
            raise ValidationError(f"Classroom {instance.classroom} is already occupied at this time.")

    # 2. Validate Teacher Availability
    teacher = instance.subject_assignment.teacher
    if teacher:
        teacher_conflicts = Timetable.objects.filter(
            subject_assignment__teacher=teacher,
            day_of_week=instance.day_of_week,
            class_time=instance.class_time,
            effective_from__lte=instance.effective_from
        ).exclude(pk=instance.pk)

        if instance.effective_to:
            teacher_conflicts = teacher_conflicts.filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=instance.effective_from)
            )

        if teacher_conflicts.exists():
            raise ValidationError(f"Teacher {teacher} is already assigned to another class at this time.")


@receiver(post_save, sender=Timetable)
def timetable_post_save(sender, instance, created, **kwargs):
    """
    Check for scheduling conflicts (double check) and notify teacher.
    """
    if created:
        # Notify teacher
        teacher = instance.subject_assignment.teacher
        if teacher:
            # TODO: Send notification to teacher
            print(f"Notification: New class assigned to {teacher} on {instance.day_of_week} at {instance.class_time}")


@receiver(post_save, sender=SubjectAssignment)
def subject_assignment_post_save(sender, instance, created, **kwargs):
    """
    Calculate teacher workload and send notification to teacher.
    """
    teacher = instance.teacher
    if teacher:
        # Calculate workload (e.g., total hours assigned)
        # This is a placeholder for actual workload calculation logic
        assignments = SubjectAssignment.objects.filter(teacher=teacher)
        total_credits = sum(a.subject.credits for a in assignments)
        # TODO: Update teacher's workload record if exists
        
        if created:
            # TODO: Send notification to teacher
            print(f"Notification: You have been assigned to teach {instance.subject.name} for {instance.class_obj.name}")
