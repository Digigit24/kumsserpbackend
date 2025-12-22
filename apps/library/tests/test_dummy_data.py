from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.core.models import College, AcademicYear
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.library.models import (
    BookCategory,
    Book,
    LibraryMember,
    LibraryCard,
    BookIssue,
    BookReturn,
    LibraryFine,
    BookReservation,
    IssueStatus,
    MemberType,
)


class LibraryDummyDataTest(TestCase):
    """Build a dummy library graph and verify relationships and signals."""

    def setUp(self):
        self.college = College.objects.create(
            code="LIB",
            name="Library College",
            short_name="LIB",
            email="info@lib.test",
            phone="9999999998",
            address_line1="123 Library St",
            city="City",
            state="State",
            pincode="000001",
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
        self.faculty = Faculty.objects.create(
            college=self.college,
            code="SCI",
            name="Science",
            short_name="SCI",
            display_order=1,
        )
        self.program = Program.objects.create(
            college=self.college,
            faculty=self.faculty,
            code="BSC",
            name="B.Sc",
            short_name="BSC",
            program_type="ug",
            duration=3,
            duration_type="year",
            total_credits=120,
            display_order=1,
        )

        self.student_user = User.objects.create_user(
            username="student_lib",
            email="student@lib.test",
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
            admission_number="ADM-LIB-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-LIB-001",
            program=self.program,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student@lib.test",
        )

        self.teacher_user = User.objects.create_user(
            username="teacher_lib",
            email="teacher@lib.test",
            password="dummy-pass",
            first_name="Tea",
            last_name="Cher",
            college=self.college,
            user_type=UserType.TEACHER,
            is_active=True,
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            college=self.college,
            employee_id="EMP-LIB-001",
            joining_date=date(2025, 6, 1),
            faculty=self.faculty,
            first_name="Tea",
            last_name="Cher",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            email="teacher@lib.test",
            phone="7777777781",
        )

        self.category = BookCategory.objects.create(
            college=self.college,
            name="Science",
            code="SCI",
        )
        self.book = Book.objects.create(
            college=self.college,
            category=self.category,
            title="Physics 101",
            author="Isaac Newton",
            quantity=5,
            available_quantity=5,
            publication_year=2020,
        )

        self.student_member = LibraryMember.objects.create(
            college=self.college,
            member_type=MemberType.STUDENT,
            student=self.student,
            member_id="MEM-STU-001",
            joining_date=date(2025, 6, 2),
        )
        self.teacher_member = LibraryMember.objects.create(
            college=self.college,
            member_type=MemberType.TEACHER,
            teacher=self.teacher,
            member_id="MEM-TEA-001",
            joining_date=date(2025, 6, 3),
            max_books_allowed=5,
        )
        self.card = LibraryCard.objects.create(
            member=self.student_member,
            card_number="CARD-001",
            issue_date=date(2025, 6, 2),
            valid_until=date(2026, 6, 1),
        )

        self.issue = BookIssue.objects.create(
            book=self.book,
            member=self.student_member,
            issue_date=date(2025, 6, 10),
            due_date=date(2025, 6, 20),
        )
        self.return_record = BookReturn.objects.create(
            issue=self.issue,
            return_date=date(2025, 6, 25),  # 5 days late
            fine_amount=Decimal('0.00'),
            damage_charges=Decimal('0.00'),
            remarks="Returned in good condition",
        )
        self.reservation = BookReservation.objects.create(
            book=self.book,
            member=self.teacher_member,
            reservation_date=date(2025, 6, 5),
        )
        self.fine = LibraryFine.objects.first()

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(BookCategory.objects.count(), 1)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(LibraryMember.objects.count(), 2)
        self.assertEqual(LibraryCard.objects.count(), 1)
        self.assertEqual(BookIssue.objects.count(), 1)
        self.assertEqual(BookReturn.objects.count(), 1)
        self.assertEqual(BookReservation.objects.count(), 1)
        self.assertGreaterEqual(LibraryFine.objects.count(), 1)

        # Inventory updates via signals
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_quantity, 5)

        # Issue status updated on return
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.status, IssueStatus.RETURNED)
        self.assertEqual(self.issue.return_date, self.return_record.return_date)

        # Fine computed for late return (5 days * 5)
        self.assertIsNotNone(self.fine)
        self.assertEqual(self.fine.amount, Decimal('25.00'))
        self.assertEqual(self.fine.book_issue, self.issue)

        # __str__ calls
        str(self.category)
        str(self.book)
        str(self.student_member)
        str(self.teacher_member)
        str(self.card)
        str(self.issue)
        str(self.return_record)
        str(self.fine)
        str(self.reservation)
