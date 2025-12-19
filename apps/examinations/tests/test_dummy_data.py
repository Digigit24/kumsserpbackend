from datetime import date, time

from django.test import TestCase

from apps.core.models import College, AcademicYear
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import (
    Faculty,
    Program,
    AcademicSession,
    Class,
    Section,
    Subject,
    Classroom,
)
from apps.teachers.models import Teacher
from apps.students.models import Student
from apps.examinations.models import (
    MarksGrade,
    ExamType,
    Exam,
    ExamSchedule,
    ExamAttendance,
    AdmitCard,
    MarksRegister,
    StudentMarks,
    ExamResult,
    ProgressCard,
    MarkSheet,
    TabulationSheet,
)


class ExaminationsDummyDataTest(TestCase):
    """Build a dummy examination graph and verify relationships."""

    def setUp(self):
        self.college = College.objects.create(
            code="EXM",
            name="Exam College",
            short_name="EXM",
            email="info@exm.test",
            phone="9999999995",
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
        self.classroom = Classroom.objects.create(
            college=self.college,
            code="R101",
            name="Room 101",
            room_type="classroom",
            capacity=60,
        )
        self.teacher_user = User.objects.create_user(
            username="teacher_exm",
            email="teacher@exm.test",
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
            employee_id="EMP-EXM-001",
            joining_date=date(2025, 6, 1),
            faculty=self.faculty,
            first_name="Teach",
            last_name="Er",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            email="teacher@exm.test",
            phone="7777777779",
        )
        self.student_user = User.objects.create_user(
            username="student_exm",
            email="student@exm.test",
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
            admission_number="ADM-EXM-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-EXM-001",
            program=self.program,
            current_class=self.class_obj,
            current_section=self.section,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student@exm.test",
        )

        self.grade = MarksGrade.objects.create(
            college=self.college,
            name="Excellent",
            grade="A",
            min_percentage=85,
            max_percentage=100,
            grade_point=4.0,
        )
        self.exam_type = ExamType.objects.create(
            college=self.college,
            name="Midterm",
            code="MID",
        )
        self.exam = Exam.objects.create(
            college=self.college,
            name="Midterm Exam",
            exam_type=self.exam_type,
            class_obj=self.class_obj,
            academic_session=self.session,
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 15),
        )
        self.schedule = ExamSchedule.objects.create(
            exam=self.exam,
            subject=self.subject,
            date=date(2025, 7, 5),
            start_time=time(10, 0),
            end_time=time(13, 0),
            classroom=self.classroom,
            invigilator=self.teacher,
            max_marks=100,
        )
        self.exam_attendance = ExamAttendance.objects.create(
            exam_schedule=self.schedule,
            student=self.student,
            status="present",
        )
        self.admit_card = AdmitCard.objects.create(
            student=self.student,
            exam=self.exam,
            card_number="ADM-CARD-1",
            issue_date=date(2025, 6, 25),
        )
        self.register = MarksRegister.objects.create(
            exam=self.exam,
            subject=self.subject,
            section=self.section,
            max_marks=100,
            pass_marks=40,
        )
        self.student_marks = StudentMarks.objects.create(
            register=self.register,
            student=self.student,
            theory_marks=80,
            practical_marks=10,
            internal_marks=5,
            total_marks=95,
            grade=self.grade.grade,
            is_absent=False,
        )
        self.exam_result = ExamResult.objects.create(
            student=self.student,
            exam=self.exam,
            total_marks=100,
            marks_obtained=95,
            percentage=95,
            grade=self.grade.grade,
            result_status="pass",
            rank=1,
        )
        self.progress_card = ProgressCard.objects.create(
            student=self.student,
            exam=self.exam,
            issue_date=date(2025, 7, 20),
        )
        self.mark_sheet = MarkSheet.objects.create(
            student=self.student,
            exam=self.exam,
            sheet_number="MS-1",
            issue_date=date(2025, 7, 21),
        )
        self.tabulation_sheet = TabulationSheet.objects.create(
            exam=self.exam,
            class_obj=self.class_obj,
            section=self.section,
            issue_date=date(2025, 7, 22),
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        def count(model):
            manager = model.objects
            return manager.all_colleges().count() if hasattr(manager, "all_colleges") else manager.count()

        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(count(MarksGrade), 1)
        self.assertEqual(count(ExamType), 1)
        self.assertEqual(count(Exam), 1)
        self.assertEqual(ExamSchedule.objects.count(), 1)
        self.assertEqual(ExamAttendance.objects.count(), 1)
        self.assertEqual(AdmitCard.objects.count(), 1)
        self.assertEqual(MarksRegister.objects.count(), 1)
        self.assertEqual(StudentMarks.objects.count(), 1)
        self.assertEqual(ExamResult.objects.count(), 1)
        self.assertEqual(ProgressCard.objects.count(), 1)
        self.assertEqual(MarkSheet.objects.count(), 1)
        self.assertEqual(TabulationSheet.objects.count(), 1)

        # Relationships
        self.assertEqual(self.schedule.exam, self.exam)
        self.assertEqual(self.exam_attendance.student, self.student)
        self.assertEqual(self.student_marks.register, self.register)
        self.assertEqual(self.exam_result.exam, self.exam)
        self.assertEqual(self.mark_sheet.student, self.student)
        self.assertEqual(self.tabulation_sheet.class_obj, self.class_obj)

        # __str__ should not raise
        str(self.grade)
        str(self.exam_type)
        str(self.exam)
        str(self.schedule)
        str(self.exam_attendance)
        str(self.admit_card)
        str(self.register)
        str(self.student_marks)
        str(self.exam_result)
        str(self.progress_card)
        str(self.mark_sheet)
        str(self.tabulation_sheet)
