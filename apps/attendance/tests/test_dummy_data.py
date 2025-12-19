from datetime import date, time

from django.test import TestCase

from apps.core.models import College, AcademicYear, AcademicSession
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program, Class, Section, Subject, SubjectAssignment, ClassTime
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.attendance.models import (
    StudentAttendance,
    SubjectAttendance,
    StaffAttendance,
    AttendanceNotification,
)


class AttendanceDummyDataTest(TestCase):
    """
    Build minimal attendance-related data and verify relationships.
    """

    def setUp(self):
        self.college = College.objects.create(
            code="ATT",
            name="Attendance College",
            short_name="ATT",
            email="info@att.test",
            phone="9999999992",
            address_line1="123 Street",
            city="City",
            state="State",
            pincode="000000",
            country="Testland",
        )
        set_current_college_id(self.college.id)

        self.year = AcademicYear.objects.create(
            college=self.college,
            year="2025-2026",
            start_date=date(2025, 6, 1),
            end_date=date(2026, 5, 31),
            is_current=True,
        )
        self.session = AcademicSession.objects.create(
            college=self.college,
            academic_year=self.year,
            name="Semester 1",
            semester=1,
            start_date=date(2025, 6, 1),
            end_date=date(2025, 11, 30),
            is_current=True,
        )
        self.faculty = Faculty.objects.create(
            college=self.college,
            code="ENG",
            name="Engineering",
            short_name="ENG",
            display_order=1,
        )
        self.program = Program.objects.create(
            college=self.college,
            faculty=self.faculty,
            code="BTECH",
            name="B.Tech",
            short_name="BTECH",
            program_type="ug",
            duration=4,
            duration_type="year",
            total_credits=160,
            display_order=1,
        )
        self.class_obj = Class.objects.create(
            college=self.college,
            program=self.program,
            academic_session=self.session,
            name="BTECH-CS Sem 1",
            semester=1,
            year=1,
            max_students=60,
        )
        self.section = Section.objects.create(
            class_obj=self.class_obj,
            name="A",
            max_students=60,
        )
        self.subject = Subject.objects.create(
            college=self.college,
            code="CS101",
            name="Computer Science",
            short_name="CS",
            subject_type="theory",
            credits="4.00",
            theory_hours=4,
            practical_hours=0,
            max_marks=100,
            pass_marks=40,
        )
        self.teacher_user = User.objects.create_user(
            username="teacher_att",
            email="teacher@att.test",
            password="dummy-pass",
            first_name="Teach",
            last_name="Er",
            college=self.college,
            user_type=UserType.TEACHER,
            is_active=True,
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            college=self.college,
            employee_id="EMP-ATT-001",
            joining_date=date(2025, 6, 1),
            faculty=self.faculty,
            first_name="Teach",
            last_name="Er",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            email="teacher@att.test",
            phone="7777777778",
        )
        self.student_user = User.objects.create_user(
            username="student_att",
            email="student@att.test",
            password="dummy-pass",
            first_name="Stu",
            last_name="Dent",
            college=self.college,
            user_type=UserType.STUDENT,
            is_active=True,
        )
        self.student = Student.objects.create(
            user=self.student_user,
            college=self.college,
            admission_number="ADM-ATT-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-ATT-001",
            program=self.program,
            current_class=self.class_obj,
            current_section=self.section,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student@att.test",
        )
        self.class_time = ClassTime.objects.create(
            college=self.college,
            period_number=1,
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_break=False,
        )
        self.assignment = SubjectAssignment.objects.create(
            subject=self.subject,
            class_obj=self.class_obj,
            section=self.section,
            teacher=self.teacher_user,
            is_optional=False,
        )

        self.student_attendance = StudentAttendance.objects.create(
            student=self.student,
            class_obj=self.class_obj,
            section=self.section,
            date=date(2025, 6, 5),
            status="present",
            marked_by=self.teacher_user,
        )
        self.subject_attendance = SubjectAttendance.objects.create(
            student=self.student,
            subject_assignment=self.assignment,
            date=date(2025, 6, 5),
            period=self.class_time,
            status="present",
            marked_by=self.teacher,
        )
        self.staff_attendance = StaffAttendance.objects.create(
            teacher=self.teacher,
            date=date(2025, 6, 5),
            status="present",
            marked_by=self.teacher_user,
        )
        self.notification = AttendanceNotification.objects.create(
            attendance=self.student_attendance,
            recipient_type="parent",
            recipient=self.teacher_user,  # dummy recipient
            notification_type="email",
            status="sent",
            message="Attendance marked",
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        def count(model):
            manager = model.objects
            return manager.all_colleges().count() if hasattr(manager, "all_colleges") else manager.count()

        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(count(AcademicYear), 1)
        self.assertEqual(count(AcademicSession), 1)
        self.assertEqual(count(Faculty), 1)
        self.assertEqual(count(Program), 1)
        self.assertEqual(count(Class), 1)
        self.assertEqual(Section.objects.count(), 1)
        self.assertEqual(count(Subject), 1)
        self.assertEqual(count(Teacher), 1)
        self.assertEqual(count(Student), 1)
        self.assertEqual(count(ClassTime), 1)
        self.assertEqual(SubjectAssignment.objects.count(), 1)
        self.assertEqual(StudentAttendance.objects.count(), 1)
        self.assertEqual(SubjectAttendance.objects.count(), 1)
        self.assertEqual(StaffAttendance.objects.count(), 1)
        self.assertEqual(AttendanceNotification.objects.count(), 1)

        # Relationship sanity
        self.assertEqual(self.student_attendance.student, self.student)
        self.assertEqual(self.subject_attendance.subject_assignment, self.assignment)
        self.assertEqual(self.staff_attendance.teacher, self.teacher)
        self.assertEqual(self.notification.attendance, self.student_attendance)

        # __str__ should not raise
        str(self.student_attendance)
        str(self.subject_attendance)
        str(self.staff_attendance)
        str(self.notification)
