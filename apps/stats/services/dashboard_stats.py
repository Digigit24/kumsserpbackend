from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.accounts.models import User
from apps.academic.models import Class
from apps.attendance.models import StudentAttendance, StaffAttendance
from apps.fees.models import FeeCollection, FeeStructure
from apps.accounting.models import Expense
from apps.examinations.models import ExamResult, Exam
from apps.teachers.models import Assignment
from apps.library.models import BookIssue


class DashboardStatsService:
    """Service class for dashboard overview statistics"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_dashboard_overview(self):
        """Get complete dashboard statistics overview"""
        today = timezone.now().date()
        first_day_of_month = today.replace(day=1)

        # Quick stats - use all_colleges() to bypass scoping, then filter
        total_students = Student.objects.filter(
            college_id=self.college_id,
            is_active=True
        ).count()

        total_teachers = Teacher.objects.filter(
            college_id=self.college_id,
            is_active=True
        ).count()

        total_staff = User.objects.filter(
            college_id=self.college_id,
            is_active=True,
            user_type='STAFF'
        ).count()

        active_classes = Class.objects.filter(
            college_id=self.college_id,
            is_active=True
        ).count()

        # Today's attendance stats
        today_student_attendance = StudentAttendance.objects.filter(
            student__college_id=self.college_id,
            date=today
        )

        today_total_student_records = today_student_attendance.count()
        today_present_students = today_student_attendance.filter(status='PRESENT').count()
        today_absent_students = today_student_attendance.filter(status='ABSENT').count()

        today_student_attendance_rate = (
            (today_present_students / today_total_student_records * 100)
            if today_total_student_records > 0 else 0
        )

        today_staff_attendance = StaffAttendance.objects.filter(
            teacher__college_id=self.college_id,
            date=today
        )

        today_total_staff_records = today_staff_attendance.count()
        today_present_staff = today_staff_attendance.filter(status='PRESENT').count()

        today_staff_attendance_rate = (
            (today_present_staff / today_total_staff_records * 100)
            if today_total_staff_records > 0 else 0
        )

        # Financial summary - This month
        fee_collections_this_month = FeeCollection.objects.filter(
            student__college_id=self.college_id,
            status='COMPLETED',
            payment_date__gte=first_day_of_month,
            payment_date__lte=today
        )

        total_fee_collected_this_month = fee_collections_this_month.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        total_fee_outstanding = FeeStructure.objects.filter(
            student__college_id=self.college_id,
            student__is_active=True,
            is_paid=False
        ).aggregate(
            total=Coalesce(Sum('balance'), Decimal('0'))
        )['total']

        total_expenses_this_month = Expense.objects.filter(
            college_id=self.college_id,
            is_active=True,
            date__gte=first_day_of_month,
            date__lte=today
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        # Academic summary
        recent_exam_results = ExamResult.objects.filter(
            student__college_id=self.college_id,
            exam__is_published=True
        ).order_by('-created_at')[:100]

        average_student_performance = recent_exam_results.aggregate(
            avg=Avg('percentage')
        )['avg'] or 0

        upcoming_exams = Exam.objects.filter(
            class_obj__college_id=self.college_id,
            start_date__gte=today,
            start_date__lte=today + timedelta(days=30)
        ).count()

        pending_assignments = Assignment.objects.filter(
            teacher__college_id=self.college_id,
            is_active=True,
            due_date__gte=today
        ).count()

        # Library summary
        books_issued_today = BookIssue.objects.filter(
            book__college_id=self.college_id,
            issue_date=today
        ).count()

        overdue_books = BookIssue.objects.filter(
            book__college_id=self.college_id,
            status='ISSUED',
            due_date__lt=today
        ).count()

        # Recent activity counts (last 7 days)
        seven_days_ago = today - timedelta(days=7)

        recent_admissions = Student.objects.filter(
            college_id=self.college_id,
            admission_date__gte=seven_days_ago,
            admission_date__lte=today
        ).count()

        recent_fee_payments = FeeCollection.objects.filter(
            student__college_id=self.college_id,
            status='COMPLETED',
            payment_date__gte=seven_days_ago,
            payment_date__lte=today
        ).count()

        return {
            # Quick stats
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_staff': total_staff,
            'active_classes': active_classes,

            # Today's stats
            'today_student_attendance_rate': round(today_student_attendance_rate, 2),
            'today_staff_attendance_rate': round(today_staff_attendance_rate, 2),
            'today_present_students': today_present_students,
            'today_absent_students': today_absent_students,

            # Financial summary
            'total_fee_collected_this_month': total_fee_collected_this_month,
            'total_fee_outstanding': total_fee_outstanding,
            'total_expenses_this_month': total_expenses_this_month,

            # Academic summary
            'average_student_performance': round(float(average_student_performance), 2),
            'upcoming_exams': upcoming_exams,
            'pending_assignments': pending_assignments,

            # Library summary
            'books_issued_today': books_issued_today,
            'overdue_books': overdue_books,

            # Recent activity counts
            'recent_admissions': recent_admissions,
            'recent_fee_payments': recent_fee_payments,

            'generated_at': timezone.now(),
        }
