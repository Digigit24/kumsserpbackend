from django.db.models import Avg, Count, Sum, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from apps.teachers.models import Teacher, Assignment, AssignmentSubmission, StudyMaterial
from apps.attendance.models import StaffAttendance
from apps.academic.models import SubjectAssignment, ClassTeacher
from apps.hr.models import LeaveApplication, Payroll


class TeacherStatsService:
    """Service class for individual teacher statistics"""

    def __init__(self, teacher_id, filters=None):
        self.teacher_id = teacher_id
        self.filters = filters or {}

    def get_my_overview(self):
        """Get teacher's personal overview statistics"""
        today = timezone.now().date()

        # Get teacher
        try:
            teacher = Teacher.objects.get(id=self.teacher_id)
        except Teacher.DoesNotExist:
            return self._empty_response()

        # Classes assigned
        subject_assignments = SubjectAssignment.objects.filter(teacher_id=self.teacher_id)
        total_subjects = subject_assignments.count()
        total_classes = subject_assignments.values('class_obj').distinct().count()

        # Class teacher assignments
        class_teacher = ClassTeacher.objects.filter(teacher_id=self.teacher_id, is_current=True)
        is_class_teacher = class_teacher.exists()

        # Assignments created
        assignments = Assignment.objects.filter(teacher_id=self.teacher_id)
        total_assignments = assignments.count()
        active_assignments = assignments.filter(is_active=True, due_date__gte=today).count()

        # Assignment submissions
        submissions = AssignmentSubmission.objects.filter(assignment__teacher_id=self.teacher_id)
        total_submissions = submissions.count()
        pending_grading = submissions.filter(status='SUBMITTED').count()
        graded = submissions.filter(status='GRADED').count()

        # Study materials uploaded
        study_materials = StudyMaterial.objects.filter(teacher_id=self.teacher_id)
        total_materials = study_materials.count()
        total_views = study_materials.aggregate(views=Coalesce(Sum('view_count'), 0))['views']

        # Attendance
        attendance = StaffAttendance.objects.filter(teacher_id=self.teacher_id)
        total_days = attendance.count()
        present_days = attendance.filter(status='PRESENT').count()
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

        # Leave
        leaves = LeaveApplication.objects.filter(teacher_id=self.teacher_id)
        total_leaves = leaves.count()
        approved_leaves = leaves.filter(status='APPROVED').count()
        pending_leaves = leaves.filter(status='PENDING').count()

        return {
            'teacher_info': {
                'id': teacher.id,
                'name': teacher.user.get_full_name() if teacher.user else 'N/A',
                'employee_id': teacher.employee_id,
                'department': teacher.department.name if teacher.department else 'N/A',
            },
            'teaching': {
                'total_subjects': total_subjects,
                'total_classes': total_classes,
                'is_class_teacher': is_class_teacher,
                'class_teacher_of': class_teacher.first().class_obj.name if is_class_teacher else 'N/A',
            },
            'assignments': {
                'total_created': total_assignments,
                'active_assignments': active_assignments,
                'total_submissions': total_submissions,
                'pending_grading': pending_grading,
                'graded': graded,
            },
            'study_materials': {
                'total_uploaded': total_materials,
                'total_views': total_views,
            },
            'attendance': {
                'total_days': total_days,
                'present_days': present_days,
                'attendance_percentage': round(attendance_percentage, 2),
            },
            'leave': {
                'total_applications': total_leaves,
                'approved': approved_leaves,
                'pending': pending_leaves,
            },
            'generated_at': timezone.now(),
        }

    def get_my_classes(self):
        """Get classes taught by teacher"""
        subject_assignments = SubjectAssignment.objects.filter(
            teacher_id=self.teacher_id
        ).select_related('subject', 'class_obj', 'section')

        classes_list = []
        for assignment in subject_assignments:
            classes_list.append({
                'subject': assignment.subject.name,
                'class': assignment.class_obj.name,
                'section': assignment.section.name if assignment.section else 'All',
                'is_optional': assignment.is_optional,
            })

        return {
            'classes': classes_list,
            'total_classes': len(classes_list),
        }

    def get_my_assignments(self):
        """Get assignments created by teacher"""
        assignments = Assignment.objects.filter(
            teacher_id=self.teacher_id
        ).select_related('subject', 'class_obj').order_by('-created_at')

        assignments_list = []
        for assignment in assignments:
            submissions = AssignmentSubmission.objects.filter(assignment=assignment)
            total_students = submissions.count()
            submitted = submissions.filter(status__in=['SUBMITTED', 'GRADED']).count()

            assignments_list.append({
                'title': assignment.title,
                'subject': assignment.subject.name,
                'class': assignment.class_obj.name,
                'due_date': assignment.due_date,
                'max_marks': assignment.max_marks,
                'total_students': total_students,
                'submitted': submitted,
                'pending': total_students - submitted,
                'status': 'Active' if assignment.is_active else 'Inactive',
            })

        return {
            'assignments': assignments_list,
            'total_assignments': len(assignments_list),
        }

    def get_my_attendance(self):
        """Get teacher's attendance records"""
        from_date = self.filters.get('from_date', timezone.now().replace(day=1).date())
        to_date = self.filters.get('to_date', timezone.now().date())

        attendance = StaffAttendance.objects.filter(
            teacher_id=self.teacher_id,
            date__gte=from_date,
            date__lte=to_date
        ).order_by('-date')

        records = []
        for record in attendance:
            records.append({
                'date': record.date,
                'status': record.status,
                'check_in_time': record.check_in_time,
                'check_out_time': record.check_out_time,
            })

        return {
            'records': records,
            'total_records': len(records),
        }

    def _empty_response(self):
        return {
            'error': 'Teacher not found',
            'generated_at': timezone.now(),
        }
