from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.core.models import College, AcademicYear, AcademicSession
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program, Class, Section, Subject
from apps.students.models import Student
from apps.teachers.models import (
    Teacher,
    StudyMaterial,
    Assignment,
    AssignmentSubmission,
    Homework,
    HomeworkSubmission,
)


class TeacherDummyDataTest(TestCase):
    """
    Build a minimal teacher graph with dummy data and ensure relationships hold.
    """

    def setUp(self):
        self.college = College.objects.create(
            code="TCH",
            name="Teacher College",
            short_name="TCH",
            email="info@teacher.test",
            phone="9999999991",
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
            username="teacher_dummy",
            email="teacher@tch.test",
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
            employee_id="EMP001",
            joining_date=date(2025, 6, 1),
            faculty=self.faculty,
            first_name="Teach",
            last_name="Er",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            email="teacher@tch.test",
            phone="7777777777",
        )
        self.student_user = User.objects.create_user(
            username="student_teacher_dummy",
            email="student_teacher@tch.test",
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
            admission_number="ADM-TCH-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-TCH-001",
            program=self.program,
            current_class=self.class_obj,
            current_section=self.section,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student_teacher@tch.test",
        )
        self.study_material = StudyMaterial.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            class_obj=self.class_obj,
            section=self.section,
            title="Intro to CS",
            description="Basics",
            content_type="pdf",
            file=SimpleUploadedFile("intro.pdf", b"dummy"),
        )
        self.assignment = Assignment.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            class_obj=self.class_obj,
            section=self.section,
            title="Assignment 1",
            description="Solve problems",
            due_date=date(2025, 7, 1),
            max_marks=100,
        )
        # Assignment signal may create submissions; ensure at least one exists
        AssignmentSubmission.objects.get_or_create(
            assignment=self.assignment,
            student=self.student,
            defaults={"status": "submitted"},
        )
        self.homework = Homework.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            class_obj=self.class_obj,
            section=self.section,
            title="Homework 1",
            description="Read chapter 1",
            due_date=date(2025, 6, 15),
        )
        HomeworkSubmission.objects.get_or_create(
            homework=self.homework,
            student=self.student,
            defaults={"status": "completed"},
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
        self.assertEqual(count(StudyMaterial), 1)
        self.assertEqual(count(Assignment), 1)
        self.assertGreaterEqual(AssignmentSubmission.objects.count(), 1)
        self.assertEqual(count(Homework), 1)
        self.assertGreaterEqual(HomeworkSubmission.objects.count(), 1)

        # Relationship sanity
        self.assertEqual(self.study_material.teacher, self.teacher)
        self.assertEqual(self.assignment.class_obj, self.class_obj)
        self.assertEqual(self.homework.section, self.section)

        # __str__ should not raise
        str(self.teacher)
        str(self.study_material)
        str(self.assignment)
        str(AssignmentSubmission.objects.first())
        str(self.homework)
        str(HomeworkSubmission.objects.first())
