from datetime import date, time

from django.test import TestCase
from django.utils import timezone

from apps.core.models import College, AcademicYear, AcademicSession
from apps.accounts.models import User, UserType
from apps.academic.models import (
    Faculty,
    Program,
    Class,
    Section,
    Subject,
    OptionalSubject,
    SubjectAssignment,
    Classroom,
    ClassTime,
    Timetable,
    LabSchedule,
    ClassTeacher,
)


class AcademicDummyDataTest(TestCase):
    """
    Smoke test that builds a minimal academic graph with dummy data.
    Ensures models can be created and linked without errors.
    """

    def setUp(self):
        self.college = College.objects.create(
            code="ACD",
            name="Academic College",
            short_name="ACD",
            email="info@acd.test",
            phone="1234567890",
            address_line1="123 Street",
            city="City",
            state="State",
            pincode="000000",
            country="Testland",
        )
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
        self.teacher = User.objects.create_user(
            username="teacher_dummy",
            email="teacher@acd.test",
            password="dummy-pass",
            first_name="Teach",
            last_name="Er",
            college=self.college,
            user_type=UserType.TEACHER,
            is_active=True,
        )
        self.faculty = Faculty.objects.create(
            college=self.college,
            code="ENG",
            name="Engineering",
            short_name="ENG",
            hod=self.teacher,
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
            code="MATH101",
            name="Maths",
            short_name="MATH",
            subject_type="theory",
            credits="4.00",
            theory_hours=4,
            practical_hours=0,
            max_marks=100,
            pass_marks=40,
        )
        self.optional_group = OptionalSubject.objects.create(
            class_obj=self.class_obj,
            name="Electives",
            description="Pick one",
            min_selection=1,
            max_selection=1,
        )
        self.optional_group.subjects.add(self.subject)
        self.classroom = Classroom.objects.create(
            college=self.college,
            code="R101",
            name="Room 101",
            room_type="classroom",
            building="Main",
            floor="1",
            capacity=60,
            has_projector=True,
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
            teacher=self.teacher,
            is_optional=False,
        )
        self.timetable = Timetable.objects.create(
            class_obj=self.class_obj,
            section=self.section,
            subject_assignment=self.assignment,
            day_of_week=1,
            class_time=self.class_time,
            classroom=self.classroom,
            effective_from=date(2025, 6, 1),
        )
        self.lab = LabSchedule.objects.create(
            subject_assignment=self.assignment,
            section=self.section,
            day_of_week=3,
            start_time=time(12, 0),
            end_time=time(14, 0),
            classroom=self.classroom,
            batch_name="Batch A",
            effective_from=date(2025, 6, 2),
        )
        self.class_teacher = ClassTeacher.objects.create(
            class_obj=self.class_obj,
            section=self.section,
            teacher=self.teacher,
            assigned_from=date(2025, 6, 1),
            assigned_to=None,
            is_current=True,
        )

    def test_dummy_graph_created(self):
        def count(model):
            manager = model.objects
            return manager.all_colleges().count() if hasattr(manager, "all_colleges") else manager.count()

        # Core counts (use all_colleges for scoped managers)
        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(count(AcademicYear), 1)
        self.assertEqual(count(AcademicSession), 1)
        self.assertEqual(count(Faculty), 1)
        self.assertEqual(count(Program), 1)
        self.assertEqual(count(Class), 1)
        self.assertEqual(Section.objects.count(), 1)
        self.assertEqual(count(Subject), 1)
        self.assertEqual(OptionalSubject.objects.count(), 1)
        self.assertEqual(SubjectAssignment.objects.count(), 1)
        self.assertEqual(count(Classroom), 1)
        self.assertEqual(count(ClassTime), 1)
        self.assertEqual(Timetable.objects.count(), 1)
        self.assertEqual(LabSchedule.objects.count(), 1)
        self.assertEqual(ClassTeacher.objects.count(), 1)

        # Relationships
        self.assertEqual(
            Subject.objects.all_colleges().filter(optional_groups=self.optional_group).count(),
            1,
        )
        self.assertEqual(self.section.class_obj, self.class_obj)
        self.assertEqual(self.assignment.teacher, self.teacher)
        self.assertEqual(self.timetable.class_time, self.class_time)
        self.assertEqual(self.lab.classroom, self.classroom)
        self.assertTrue(self.class_teacher.is_current)

        # __str__ should not crash
        str(self.faculty)
        str(self.program)
        str(self.class_obj)
        str(self.section)
        str(self.subject)
        str(self.optional_group)
        str(self.assignment)
        str(self.classroom)
        str(self.class_time)
        str(self.timetable)
        str(self.lab)
        str(self.class_teacher)
