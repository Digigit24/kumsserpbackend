from datetime import date, datetime

from django.test import TestCase

from apps.core.models import College, AcademicYear
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program, AcademicSession, Class, Section, Subject
from apps.students.models import Student
from apps.online_exam.models import (
    QuestionBank,
    Question,
    QuestionOption,
    OnlineExam,
    ExamQuestion,
    StudentExamAttempt,
    StudentAnswer,
)


class OnlineExamDummyDataTest(TestCase):
    """Build a dummy online exam graph and verify relationships."""

    def setUp(self):
        self.college = College.objects.create(
            code="OEX",
            name="Online Exam College",
            short_name="OEX",
            email="info@oex.test",
            phone="9999999996",
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
        self.student_user = User.objects.create_user(
            username="student_oex",
            email="student@oex.test",
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
            admission_number="ADM-OEX-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-OEX-001",
            program=self.program,
            current_class=self.class_obj,
            current_section=self.section,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student@oex.test",
        )

        self.bank = QuestionBank.objects.create(
            college=self.college,
            subject=self.subject,
            name="CS Fundamentals",
            description="Basic CS questions",
        )
        self.question = Question.objects.create(
            bank=self.bank,
            question_type="MCQ",
            question_text="What is 2+2?",
            correct_answer="4",
            difficulty_level="easy",
            marks=2,
            explanation="Simple addition",
        )
        self.option1 = QuestionOption.objects.create(
            question=self.question,
            option_text="4",
            is_correct=True,
        )
        self.option2 = QuestionOption.objects.create(
            question=self.question,
            option_text="5",
            is_correct=False,
        )
        self.exam = OnlineExam.objects.create(
            college=self.college,
            subject=self.subject,
            class_obj=self.class_obj,
            section=self.section,
            name="CS Quiz 1",
            description="Quiz on basics",
            duration=30,
            total_marks=2,
            pass_marks=1,
            start_datetime=datetime(2025, 7, 1, 10, 0),
            end_datetime=datetime(2025, 7, 1, 10, 30),
            negative_marking=False,
            allow_review=True,
            randomize_questions=False,
            is_published=True,
        )
        self.exam_question = ExamQuestion.objects.create(
            exam=self.exam,
            question=self.question,
            marks=2,
            order=1,
        )
        self.attempt = StudentExamAttempt.objects.create(
            exam=self.exam,
            student=self.student,
            start_time=datetime(2025, 7, 1, 10, 0),
            status="in_progress",
        )
        self.answer = StudentAnswer.objects.create(
            attempt=self.attempt,
            question=self.question,
            selected_option=self.option1,
            is_correct=True,
            marks_awarded=2,
            time_taken=30,
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        def count(model):
            manager = model.objects
            return manager.all_colleges().count() if hasattr(manager, "all_colleges") else manager.count()

        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(count(QuestionBank), 1)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(QuestionOption.objects.count(), 2)
        self.assertEqual(count(OnlineExam), 1)
        self.assertEqual(ExamQuestion.objects.count(), 1)
        self.assertEqual(StudentExamAttempt.objects.count(), 1)
        self.assertEqual(StudentAnswer.objects.count(), 1)

        # Relationships
        self.assertEqual(self.bank.subject, self.subject)
        self.assertEqual(self.question.bank, self.bank)
        self.assertEqual(self.exam_question.exam, self.exam)
        self.assertEqual(self.answer.attempt, self.attempt)

        # __str__ calls
        str(self.bank)
        str(self.question)
        str(self.option1)
        str(self.exam)
        str(self.exam_question)
        str(self.attempt)
        str(self.answer)
