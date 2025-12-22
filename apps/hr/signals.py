"""
Signals for HR app.
Handles leave approvals, balances, attendance updates, and payroll processing.
"""
from datetime import timedelta
from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.attendance.models import StaffAttendance
from apps.core.models import AcademicYear
from .models import (
    LeaveApplication,
    LeaveApproval,
    LeaveBalance,
    Payroll,
    PayrollItem,
    Payslip,
)


def _days_between(start_date, end_date):
    return (end_date - start_date).days + 1


@receiver(post_save, sender=LeaveApplication)
def leave_application_post_save(sender, instance, created, **kwargs):
    """
    On creation, ensure an approval record exists and notify placeholder.
    """
    if created:
        LeaveApproval.objects.get_or_create(
            application=instance,
            defaults={
                'status': 'pending',
                'approval_date': instance.applied_date,
                'approved_by': instance.created_by,
                'remarks': None,
            },
        )
    print(f"[HR] Leave application {instance.id} submitted by {instance.teacher}.")


def _apply_leave_balance(application):
    """
    Update leave balance based on approved application.
    """
    teacher = application.teacher
    leave_type = application.leave_type
    academic_year = AcademicYear.objects.filter(college=teacher.college, is_current=True).first()

    balance, _ = LeaveBalance.objects.get_or_create(
        teacher=teacher,
        leave_type=leave_type,
        academic_year=academic_year,
        defaults={
            'total_days': leave_type.max_days_per_year,
            'used_days': 0,
            'balance_days': leave_type.max_days_per_year,
            'created_by': application.created_by,
            'updated_by': application.updated_by,
        },
    )
    balance.used_days += application.total_days
    balance.balance_days = max(0, balance.total_days - balance.used_days)
    balance.save(update_fields=['used_days', 'balance_days', 'updated_at'])


def _create_staff_attendance_for_leave(application):
    """
    Mark staff attendance as on_leave for the date range.
    """
    current_date = application.from_date
    while current_date <= application.to_date:
        StaffAttendance.objects.get_or_create(
            teacher=application.teacher,
            date=current_date,
            defaults={
                'status': 'on_leave',
                'remarks': f"Leave: {application.leave_type.name}",
                'marked_by': application.created_by,
            },
        )
        current_date += timedelta(days=1)


@receiver(post_save, sender=LeaveApproval)
def leave_approval_post_save(sender, instance, created, **kwargs):
    """
    On approval, adjust leave balance and staff attendance.
    """
    if instance.status != 'approved':
        return

    application = instance.application
    _apply_leave_balance(application)
    _create_staff_attendance_for_leave(application)
    print(f"[HR] Leave application {application.id} approved.")


@receiver(post_save, sender=Payroll)
def payroll_post_save(sender, instance, created, **kwargs):
    """
    When payroll is processed, generate payslip and payroll items.
    """
    if instance.status != 'processed':
        return

    structure = instance.salary_structure

    # Copy salary components to payroll items if not already present
    if not instance.items.exists():
        total_allowances = Decimal('0.00')
        total_deductions = Decimal('0.00')
        for comp in structure.components.all():
            PayrollItem.objects.create(
                payroll=instance,
                component_name=comp.component_name,
                component_type=comp.component_type,
                amount=comp.amount,
                created_by=instance.created_by,
                updated_by=instance.updated_by,
            )
            if comp.component_type == 'allowance':
                total_allowances += comp.amount
            else:
                total_deductions += comp.amount

        instance.total_allowances = total_allowances
        instance.total_deductions = total_deductions
        instance.net_salary = instance.gross_salary + total_allowances - total_deductions
        instance.save(update_fields=['total_allowances', 'total_deductions', 'net_salary', 'updated_at'])

    # Generate payslip if missing
    if not instance.payslips.exists():
        slip_number = f"PAY-{instance.year}{instance.month:02d}-{instance.teacher_id}"
        Payslip.objects.create(
            payroll=instance,
            slip_number=slip_number,
            issue_date=timezone.now().date(),
            created_by=instance.created_by,
            updated_by=instance.updated_by,
        )

    print(f"[HR] Payroll processed for {instance.teacher} {instance.month}/{instance.year}.")
