from django.db.models import Avg, Count, Sum, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.students.models import Student
from apps.attendance.models import StudentAttendance
from apps.examinations.models import StudentMarks, ExamResult
from apps.teachers.models import AssignmentSubmission, HomeworkSubmission
from apps.fees.models import FeeCollection, FeeStructure, FeeFine
from apps.library.models import BookIssue


class StudentStatsService:
    """Service class for individual student statistics"""

    def __init__(self, student_id, filters=None):
        self.student_id = student_id
        self.filters = filters or {}

    def get_my_overview(self):
        """Get student's personal overview statistics"""
        today = timezone.now().date()

        # Get student
        try:
            student = Student.objects.get(id=self.student_id)
        except Student.DoesNotExist:
            return self._empty_response()

        # Attendance stats
        attendance_qs = StudentAttendance.objects.filter(student_id=self.student_id)
        total_days = attendance_qs.count()
        present_days = attendance_qs.filter(status='PRESENT').count()
        absent_days = attendance_qs.filter(status='ABSENT').count()
        late_days = attendance_qs.filter(status='LATE').count()

        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

        # Academic performance
        exam_results = ExamResult.objects.filter(student_id=self.student_id)
        total_exams = exam_results.count()
        avg_percentage = exam_results.aggregate(avg=Avg('percentage'))['avg'] or 0
        latest_result = exam_results.order_by('-exam__end_date').first()

        # Assignments
        assignments = AssignmentSubmission.objects.filter(student_id=self.student_id)
        total_assignments = assignments.count()
        submitted = assignments.filter(status__in=['SUBMITTED', 'GRADED']).count()
        pending = assignments.filter(status='PENDING').count()
        avg_assignment_marks = assignments.filter(
            status='GRADED',
            marks_obtained__isnull=False
        ).aggregate(avg=Avg('marks_obtained'))['avg'] or 0

        # Fee status
        fee_structure = FeeStructure.objects.filter(student_id=self.student_id)
        total_fee = fee_structure.aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        paid_fee = fee_structure.filter(is_paid=True).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']
        balance_fee = fee_structure.aggregate(total=Coalesce(Sum('balance'), Decimal('0')))['total']

        # Library
        books_issued = BookIssue.objects.filter(student=student.id, status='ISSUED').count()
        overdue_books = BookIssue.objects.filter(
            student=student.id,
            status='ISSUED',
            due_date__lt=today
        ).count()

        return {
            'student_info': {
                'id': student.id,
                'name': student.user.get_full_name() if student.user else 'N/A',
                'admission_number': student.admission_number,
                'class': student.current_class.name if student.current_class else 'N/A',
                'roll_number': student.roll_number,
            },
            'attendance': {
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days,
                'attendance_percentage': round(attendance_percentage, 2),
            },
            'academic': {
                'total_exams': total_exams,
                'average_percentage': round(float(avg_percentage), 2),
                'latest_grade': latest_result.grade if latest_result else 'N/A',
                'latest_percentage': float(latest_result.percentage) if latest_result else 0,
            },
            'assignments': {
                'total_assignments': total_assignments,
                'submitted': submitted,
                'pending': pending,
                'average_marks': round(float(avg_assignment_marks), 2),
            },
            'fees': {
                'total_fee': total_fee,
                'paid': paid_fee,
                'balance': balance_fee,
                'payment_status': 'Paid' if balance_fee == 0 else 'Pending',
            },
            'library': {
                'books_issued': books_issued,
                'overdue_books': overdue_books,
            },
            'generated_at': timezone.now(),
        }

    def get_my_attendance_details(self):
        """Get detailed attendance records"""
        from_date = self.filters.get('from_date', timezone.now().replace(day=1).date())
        to_date = self.filters.get('to_date', timezone.now().date())

        attendance = StudentAttendance.objects.filter(
            student_id=self.student_id,
            date__gte=from_date,
            date__lte=to_date
        ).order_by('-date')

        records = []
        for record in attendance[:30]:  # Last 30 records
            records.append({
                'date': record.date,
                'status': record.status,
                'remarks': record.remarks or '',
            })

        return {
            'records': records,
            'total_records': attendance.count(),
        }

    def get_my_exam_results(self):
        """Get exam results"""
        results = ExamResult.objects.filter(
            student_id=self.student_id
        ).select_related('exam').order_by('-exam__end_date')

        exam_list = []
        for result in results:
            exam_list.append({
                'exam_name': result.exam.name,
                'exam_date': result.exam.end_date,
                'marks_obtained': float(result.marks_obtained),
                'percentage': float(result.percentage),
                'grade': result.grade,
                'result_status': result.result_status,
                'rank': result.rank,
            })

        return {
            'exams': exam_list,
            'total_exams': len(exam_list),
        }

    def get_my_fee_details(self):
        """Get fee payment details"""
        fee_collections = FeeCollection.objects.filter(
            student_id=self.student_id,
            status='COMPLETED'
        ).order_by('-payment_date')

        payments = []
        for collection in fee_collections:
            payments.append({
                'payment_date': collection.payment_date,
                'amount': collection.amount,
                'payment_method': collection.payment_method,
                'receipt_number': collection.receipt.receipt_number if hasattr(collection, 'receipt') else 'N/A',
            })

        fee_structure = FeeStructure.objects.filter(student_id=self.student_id)

        return {
            'payments': payments,
            'total_paid': fee_collections.aggregate(
                total=Coalesce(Sum('amount'), Decimal('0'))
            )['total'],
            'total_due': fee_structure.aggregate(
                total=Coalesce(Sum('balance'), Decimal('0'))
            )['total'],
        }

    def _empty_response(self):
        return {
            'error': 'Student not found',
            'generated_at': timezone.now(),
        }
