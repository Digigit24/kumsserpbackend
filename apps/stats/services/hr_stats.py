from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal

from apps.hr.models import LeaveApplication, Payroll, SalaryStructure
from apps.attendance.models import StaffAttendance
from apps.teachers.models import Teacher


class HRStatsService:
    """Service class for HR statistics calculations"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_leave_stats(self):
        """Calculate leave statistics"""
        leaves = LeaveApplication.objects.filter(
            teacher__college_id=self.college_id
        )

        if self.filters.get('from_date'):
            leaves = leaves.filter(from_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            leaves = leaves.filter(to_date__lte=self.filters['to_date'])
        if self.filters.get('department'):
            leaves = leaves.filter(teacher__department=self.filters['department'])

        total_applications = leaves.count()
        approved_count = leaves.filter(status='APPROVED').count()
        pending_count = leaves.filter(status='PENDING').count()
        rejected_count = leaves.filter(status='REJECTED').count()

        total_leave_days = leaves.filter(status='APPROVED').aggregate(
            total=Coalesce(Sum('total_days'), 0)
        )['total']

        approval_rate = (approved_count / total_applications * 100) if total_applications > 0 else 0

        # Leave type distribution
        leave_types = leaves.values('leave_type__name').annotate(
            approved_count=Count('id', filter=Q(status='APPROVED')),
            pending_count=Count('id', filter=Q(status='PENDING')),
            rejected_count=Count('id', filter=Q(status='REJECTED')),
            total_days=Coalesce(Sum('total_days', filter=Q(status='APPROVED')), 0)
        )

        leave_type_distribution = []
        for leave_type in leave_types:
            leave_type_distribution.append({
                'leave_type': leave_type['leave_type__name'] or 'N/A',
                'approved_count': leave_type['approved_count'],
                'pending_count': leave_type['pending_count'],
                'rejected_count': leave_type['rejected_count'],
                'total_days': leave_type['total_days']
            })

        return {
            'total_applications': total_applications,
            'approved_count': approved_count,
            'pending_count': pending_count,
            'rejected_count': rejected_count,
            'total_leave_days': total_leave_days,
            'approval_rate': round(approval_rate, 2),
            'leave_type_distribution': leave_type_distribution,
        }

    def get_payroll_stats(self):
        """Calculate payroll statistics"""
        # Get payroll data
        payroll_qs = Payroll.objects.filter(
            teacher__college_id=self.college_id
        )

        if self.filters.get('month'):
            payroll_qs = payroll_qs.filter(month=self.filters['month'])
        if self.filters.get('year'):
            payroll_qs = payroll_qs.filter(year=self.filters['year'])
        else:
            # Default to current year
            payroll_qs = payroll_qs.filter(year=timezone.now().year)

        total_employees = payroll_qs.values('teacher').distinct().count()

        total_gross_salary = payroll_qs.aggregate(
            total=Coalesce(Sum('gross_salary'), Decimal('0'))
        )['total']

        total_deductions = payroll_qs.aggregate(
            total=Coalesce(Sum('total_deductions'), Decimal('0'))
        )['total']

        total_net_salary = payroll_qs.aggregate(
            total=Coalesce(Sum('net_salary'), Decimal('0'))
        )['total']

        average_salary = (total_net_salary / total_employees) if total_employees > 0 else Decimal('0')

        paid_count = payroll_qs.filter(status='PAID').count()
        pending_count = payroll_qs.filter(status='PENDING').count()

        return {
            'total_employees': total_employees,
            'total_gross_salary': total_gross_salary,
            'total_deductions': total_deductions,
            'total_net_salary': total_net_salary,
            'average_salary': average_salary,
            'paid_count': paid_count,
            'pending_count': pending_count,
        }

    def get_attendance_stats(self):
        """Calculate staff attendance statistics"""
        from_date = self.filters.get('from_date', timezone.now().replace(day=1).date())
        to_date = self.filters.get('to_date', timezone.now().date())

        attendance_qs = StaffAttendance.objects.filter(
            teacher__college_id=self.college_id,
            date__gte=from_date,
            date__lte=to_date
        )

        if self.filters.get('department'):
            attendance_qs = attendance_qs.filter(teacher__department=self.filters['department'])

        total_records = attendance_qs.count()
        present_count = attendance_qs.filter(status='PRESENT').count()
        absent_count = attendance_qs.filter(status='ABSENT').count()
        late_count = attendance_qs.filter(status='LATE').count()
        leave_count = attendance_qs.filter(status='LEAVE').count()

        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0

        return {
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'leave_count': leave_count,
            'attendance_rate': round(attendance_rate, 2),
        }

    def get_all_stats(self):
        """Get all HR statistics combined"""
        return {
            'leave': self.get_leave_stats(),
            'payroll': self.get_payroll_stats(),
            'attendance': self.get_attendance_stats(),
            'generated_at': timezone.now(),
        }
