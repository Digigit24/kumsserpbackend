"""
Signals for Students app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Student, StudentGuardian, Certificate, StudentIDCard, StudentMedicalRecord

User = get_user_model()


@receiver(post_save, sender=Student)
def student_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for Student model.
    - Generate admission number if not provided
    - Create StudentMedicalRecord
    - Send admission confirmation
    - Log admission activity
    """
    if created:
        # Generate admission number if not provided (already required in model, but for safety)
        if not instance.admission_number:
            # Generate format: ADM-YEAR-SEQUENCENUMBER
            year = instance.admission_date.year
            college_code = instance.college.code
            # Simple sequential number (in production, use atomic counter or database sequence)
            count = Student.objects.filter(college=instance.college).count()
            instance.admission_number = f"ADM-{college_code}-{year}-{count:05d}"
            instance.save(update_fields=['admission_number'])

        # Create StudentMedicalRecord
        StudentMedicalRecord.objects.get_or_create(
            student=instance,
            defaults={
                'blood_group': instance.blood_group,
                'created_by': instance.created_by,
            }
        )

        # TODO: Send admission confirmation email/SMS
        print(f"Admission Confirmation: {instance.get_full_name()} admitted with {instance.admission_number}")

        # TODO: Log admission activity
        print(f"Activity Log: Student {instance.admission_number} admitted to {instance.program.name}")


@receiver(post_save, sender=StudentGuardian)
def student_guardian_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for StudentGuardian model.
    - Link Guardian user account if email exists
    - Send parent portal credentials
    - Grant parent access
    """
    if created:
        guardian = instance.guardian
        
        # Link Guardian user account if email exists and user doesn't exist yet
        if guardian.email and not guardian.user:
            try:
                # Check if user with this email already exists
                user = User.objects.get(email=guardian.email)
                guardian.user = user
                guardian.save(update_fields=['user'])
            except User.DoesNotExist:
                # TODO: Create user account for guardian and send credentials
                print(f"TODO: Create parent portal account for {guardian.get_full_name()}")

        # TODO: Send parent portal credentials
        if guardian.email:
            print(f"Parent Portal: Credentials sent to {guardian.email}")

        # TODO: Grant parent access to student data
        print(f"Access Granted: {guardian.get_full_name()} can now access {instance.student.get_full_name()}'s data")


@receiver(post_save, sender=Certificate)
def certificate_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for Certificate model.
    - Generate verification QR code
    - Generate certificate PDF
    - Send certificate
    """
    if created:
        # TODO: Generate verification QR code with verification_code
        print(f"QR Code: Generating QR for certificate {instance.certificate_number}")

        # TODO: Generate certificate PDF
        print(f"PDF Generation: Creating certificate PDF for {instance.student.get_full_name()}")

        # TODO: Send certificate to student email
        if instance.student.email:
            print(f"Certificate Sent: {instance.certificate_type} certificate sent to {instance.student.email}")


@receiver(post_save, sender=StudentIDCard)
def student_id_card_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal for StudentIDCard model.
    - Generate QR code with student details
    - Generate ID card PDF
    """
    if created or not instance.qr_code:
        # TODO: Generate QR code with student details (admission_number, name, etc.)
        student_data = {
            'admission_number': instance.student.admission_number,
            'name': instance.student.get_full_name(),
            'card_number': instance.card_number,
            'valid_until': str(instance.valid_until),
        }
        print(f"QR Code: Generating QR for ID card {instance.card_number} with data: {student_data}")

    if created or not instance.card_file:
        # TODO: Generate ID card PDF
        print(f"ID Card PDF: Creating ID card for {instance.student.get_full_name()}")
