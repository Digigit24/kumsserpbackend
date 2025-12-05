"""
Signals for Attendance app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import StudentAttendance, SubjectAttendance, StaffAttendance, AttendanceNotification


@receiver(post_save, sender=StudentAttendance)
def student_attendance_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for StudentAttendance model.
    - If 'absent' or 'late', create AttendanceNotification for parents
    - Calculate daily attendance
    - Log activity
    """
    if created or instance.status in ['absent', 'late']:
        # Create notification for parents if absent or late
        if instance.status in ['absent', 'late']:
            # Get student's guardians
            guardians = instance.student.guardians.filter(is_primary=True)
            
            for student_guardian in guardians:
                guardian = student_guardian.guardian
                if guardian.user:
                    # Create notification
                    message = f"Your ward {instance.student.get_full_name()} was marked {instance.status} on {instance.date}."
                    AttendanceNotification.objects.create(
                        attendance=instance,
                        recipient_type='parent',
                        recipient=guardian.user,
                        notification_type='sms',  # Can be configurable
                        message=message,
                        status='pending'
                    )
                    print(f"Notification created: {message}")

        # TODO: Calculate daily attendance percentage
        print(f"Daily Attendance: Calculating for {instance.student.get_full_name()}")

        # TODO: Log activity
        print(f"Activity Log: Attendance marked for {instance.student.get_full_name()} - {instance.status}")


@receiver(post_save, sender=SubjectAttendance)
def subject_attendance_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for SubjectAttendance model.
    - Calculate subject-wise attendance percentage
    - Update overall attendance
    """
    if created:
        # TODO: Calculate subject-wise attendance percentage
        subject_name = instance.subject_assignment.subject.name
        print(f"Subject Attendance: Calculating for {instance.student.get_full_name()} in {subject_name}")

        # TODO: Update overall attendance
        print(f"Overall Attendance: Updated for {instance.student.get_full_name()}")


@receiver(post_save, sender=StaffAttendance)
def staff_attendance_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for StaffAttendance model.
    - If absent without leave, send alert to admin
    - Calculate monthly attendance
    """
    if created:
        # Check if absent without leave
        if instance.status == 'absent':
            # TODO: Send alert to admin
            print(f"Alert: {instance.teacher.get_full_name()} marked absent on {instance.date} without leave application")

        # TODO: Calculate monthly attendance
        print(f"Monthly Attendance: Calculating for {instance.teacher.get_full_name()}")


# Note: Celery task for AttendanceNotification processing
# This would be in a separate tasks.py file using Celery
"""
from celery import shared_task
from .models import AttendanceNotification

@shared_task
def process_attendance_notifications():
    '''
    Celery task to process pending attendance notifications.
    - Send SMS/Email/WhatsApp
    - Update delivery status
    '''
    pending_notifications = AttendanceNotification.objects.filter(status='pending')
    
    for notification in pending_notifications:
        try:
            # TODO: Send notification based on notification_type
            if notification.notification_type == 'sms':
                # Send SMS
                pass
            elif notification.notification_type == 'email':
                # Send Email
                pass
            elif notification.notification_type == 'whatsapp':
                # Send WhatsApp
                pass
            
            # Update status
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()
            
        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()
"""
