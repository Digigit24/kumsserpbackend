from django.db.models import Avg, Count, Sum, Q, F, Case, When, FloatField, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.students.models import Student
from apps.attendance.models import StudentAttendance
from apps.examinations.models import StudentMarks, ExamResult, Exam
from apps.teachers.models import AssignmentSubmission, HomeworkSubmission, Assignment
from apps.academic.models import Subject


class AcademicStatsService:
    """Service class for academic statistics calculations"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_performance_stats(self):
        """Calculate student performance statistics"""
        # Base queryset - use all_colleges() to bypass scoping
        students_qs = Student.objects.all_colleges().filter(college_id=self.college_id, is_active=True)

        # Apply filters
        if self.filters.get('academic_year'):
            students_qs = students_qs.filter(current_class__academic_year=self.filters['academic_year'])
        if self.filters.get('program'):
            students_qs = students_qs.filter(program=self.filters['program'])
        if self.filters.get('class'):
            students_qs = students_qs.filter(current_class=self.filters['class'])

        total_students = students_qs.count()

        # Exam results stats
        exam_results = ExamResult.objects.all_colleges().filter(
            student__college_id=self.college_id,
            student__is_active=True
        )

        if self.filters.get('from_date'):
            exam_results = exam_results.filter(exam__start_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            exam_results = exam_results.filter(exam__end_date__lte=self.filters['to_date'])
        if self.filters.get('class'):
            exam_results = exam_results.filter(exam__class_obj=self.filters['class'])

        # Calculate metrics
        total_exams = exam_results.values('exam').distinct().count()
        avg_percentage = exam_results.aggregate(avg=Avg('percentage'))['avg'] or 0

        pass_count = exam_results.filter(result_status='PASS').count()
        fail_count = exam_results.filter(result_status='FAIL').count()
        total_results = exam_results.count()

        pass_percentage = (pass_count / total_results * 100) if total_results > 0 else 0

        # Grade distribution
        grade_stats = exam_results.values('grade').annotate(
            count=Count('id')
        ).order_by('grade')

        grade_distribution = []
        for grade_stat in grade_stats:
            grade_distribution.append({
                'grade': grade_stat['grade'] or 'N/A',
                'count': grade_stat['count'],
                'percentage': round((grade_stat['count'] / total_results * 100), 2) if total_results > 0 else 0
            })

        # Top performers
        top_performers_qs = exam_results.select_related('student__user').order_by('-percentage')[:10]
        top_performers = []
        for idx, result in enumerate(top_performers_qs, 1):
            top_performers.append({
                'student_id': result.student.id,
                'admission_number': result.student.admission_number,
                'student_name': result.student.user.get_full_name() if result.student.user else 'N/A',
                'percentage': float(result.percentage),
                'grade': result.grade or 'N/A',
                'rank': idx
            })

        return {
            'total_students': total_students,
            'total_exams_conducted': total_exams,
            'average_percentage': round(float(avg_percentage), 2),
            'pass_percentage': round(pass_percentage, 2),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'grade_distribution': grade_distribution,
            'top_performers': top_performers
        }

    def get_attendance_stats(self):
        """Calculate attendance statistics"""
        # Date range (default: current month)
        from_date = self.filters.get('from_date', timezone.now().replace(day=1).date())
        to_date = self.filters.get('to_date', timezone.now().date())

        attendance_qs = StudentAttendance.objects.all_colleges().filter(
            student__college_id=self.college_id,
            date__gte=from_date,
            date__lte=to_date
        )

        # Apply filters
        if self.filters.get('class'):
            attendance_qs = attendance_qs.filter(class_obj=self.filters['class'])
        if self.filters.get('section'):
            attendance_qs = attendance_qs.filter(section=self.filters['section'])

        total_records = attendance_qs.count()
        present_count = attendance_qs.filter(status='PRESENT').count()
        absent_count = attendance_qs.filter(status='ABSENT').count()
        late_count = attendance_qs.filter(status='LATE').count()
        leave_count = attendance_qs.filter(status='LEAVE').count()

        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0

        # Daily attendance trend
        daily_trend_qs = attendance_qs.values('date').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(status='PRESENT')),
            absent=Count('id', filter=Q(status='ABSENT')),
            late=Count('id', filter=Q(status='LATE')),
        ).order_by('date')

        daily_trend = []
        for day in daily_trend_qs:
            daily_trend.append({
                'date': day['date'],
                'total': day['total'],
                'present': day['present'],
                'absent': day['absent'],
                'late': day['late'],
                'attendance_rate': round((day['present'] / day['total'] * 100), 2) if day['total'] > 0 else 0
            })

        # Chronic absentees (attendance < 75%) and perfect attendance (100%)
        student_attendance = attendance_qs.values('student').annotate(
            total_days=Count('id'),
            present_days=Count('id', filter=Q(status='PRESENT')),
        )

        chronic_absentees = 0
        perfect_attendance = 0
        for student_stat in student_attendance:
            if student_stat['total_days'] > 0:
                attendance_pct = (student_stat['present_days'] / student_stat['total_days']) * 100
                if attendance_pct < 75:
                    chronic_absentees += 1
                elif attendance_pct == 100:
                    perfect_attendance += 1

        return {
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'leave_count': leave_count,
            'attendance_rate': round(attendance_rate, 2),
            'chronic_absentees_count': chronic_absentees,
            'perfect_attendance_count': perfect_attendance,
            'daily_trend': daily_trend,
        }

    def get_assignment_stats(self):
        """Calculate assignment submission statistics"""
        from_date = self.filters.get('from_date')
        to_date = self.filters.get('to_date')

        assignments_qs = Assignment.objects.all_colleges().filter(
            teacher__college_id=self.college_id,
            is_active=True
        )

        if from_date:
            assignments_qs = assignments_qs.filter(created_at__gte=from_date)
        if to_date:
            assignments_qs = assignments_qs.filter(created_at__lte=to_date)
        if self.filters.get('class'):
            assignments_qs = assignments_qs.filter(class_obj=self.filters['class'])

        total_assignments = assignments_qs.count()

        submissions_qs = AssignmentSubmission.objects.all_colleges().filter(
            assignment__teacher__college_id=self.college_id
        )

        if from_date:
            submissions_qs = submissions_qs.filter(submission_date__gte=from_date)
        if to_date:
            submissions_qs = submissions_qs.filter(submission_date__lte=to_date)

        total_submissions = submissions_qs.count()
        submitted_count = submissions_qs.filter(status='SUBMITTED').count()
        pending_count = submissions_qs.filter(status='PENDING').count()
        graded_count = submissions_qs.filter(status='GRADED').count()
        late_submissions = submissions_qs.filter(is_late=True).count()

        avg_marks = submissions_qs.filter(
            status='GRADED',
            marks_obtained__isnull=False
        ).aggregate(avg=Avg('marks_obtained'))['avg'] or 0

        submission_rate = (submitted_count / total_submissions * 100) if total_submissions > 0 else 0
        completion_rate = (graded_count / total_submissions * 100) if total_submissions > 0 else 0

        return {
            'total_assignments': total_assignments,
            'total_submissions': total_submissions,
            'submitted_count': submitted_count,
            'pending_count': pending_count,
            'graded_count': graded_count,
            'late_submissions': late_submissions,
            'submission_rate': round(submission_rate, 2),
            'average_marks': round(float(avg_marks), 2),
            'completion_rate': round(completion_rate, 2),
        }

    def get_subject_wise_performance(self):
        """Calculate subject-wise performance statistics"""
        exam_results = ExamResult.objects.all_colleges().filter(
            student__college_id=self.college_id,
            student__is_active=True
        )

        if self.filters.get('from_date'):
            exam_results = exam_results.filter(exam__start_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            exam_results = exam_results.filter(exam__end_date__lte=self.filters['to_date'])
        if self.filters.get('class'):
            exam_results = exam_results.filter(exam__class_obj=self.filters['class'])

        # Get marks grouped by subject
        marks_qs = StudentMarks.objects.all_colleges().filter(
            register__exam__in=exam_results.values('exam'),
            student__college_id=self.college_id
        ).select_related('register__subject')

        subject_stats = marks_qs.values(
            'register__subject__id',
            'register__subject__name',
            'register__subject__code'
        ).annotate(
            total_students=Count('student', distinct=True),
            average_marks=Avg('total_marks'),
            pass_count=Count('id', filter=Q(total_marks__gte=F('register__pass_marks'))),
            total_count=Count('id')
        )

        subject_wise_performance = []
        for subject in subject_stats:
            pass_percentage = 0
            if subject['total_count'] > 0:
                pass_percentage = (subject['pass_count'] / subject['total_count']) * 100

            subject_wise_performance.append({
                'subject_id': subject['register__subject__id'],
                'subject_name': subject['register__subject__name'],
                'subject_code': subject['register__subject__code'],
                'average_marks': round(float(subject['average_marks'] or 0), 2),
                'pass_percentage': round(pass_percentage, 2),
                'total_students': subject['total_students']
            })

        return subject_wise_performance

    def get_all_stats(self):
        """Get all academic statistics combined"""
        return {
            'performance': self.get_performance_stats(),
            'attendance': self.get_attendance_stats(),
            'assignments': self.get_assignment_stats(),
            'subject_wise_performance': self.get_subject_wise_performance(),
            'generated_at': timezone.now(),
        }
