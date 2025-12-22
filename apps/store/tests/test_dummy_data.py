from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.core.models import College, AcademicYear
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.store.models import (
    StoreCategory,
    StoreItem,
    Vendor,
    StockReceive,
    StoreSale,
    SaleItem,
    StoreCredit,
    PrintJob,
)


class StoreDummyDataTest(TestCase):
    """Build a dummy store graph and verify relationships and signals."""

    def setUp(self):
        self.college = College.objects.create(
            code="STR",
            name="Store College",
            short_name="STR",
            email="info@str.test",
            phone="9999999999",
            address_line1="123 Store St",
            city="City",
            state="State",
            pincode="000002",
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
            code="BUS",
            name="Business",
            short_name="BUS",
            display_order=1,
        )
        self.program = Program.objects.create(
            college=self.college,
            faculty=self.faculty,
            code="MBA",
            name="MBA",
            short_name="MBA",
            program_type="pg",
            duration=2,
            duration_type="year",
            total_credits=80,
            display_order=1,
        )

        self.student_user = User.objects.create_user(
            username="student_store",
            email="student@store.test",
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
            admission_number="ADM-STR-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-STR-001",
            program=self.program,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2006, 1, 1),
            gender="male",
            email="student@store.test",
        )

        self.teacher_user = User.objects.create_user(
            username="teacher_store",
            email="teacher@store.test",
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
            employee_id="EMP-STR-001",
            joining_date=date(2025, 6, 1),
            faculty=self.faculty,
            first_name="Tea",
            last_name="Cher",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            email="teacher@store.test",
            phone="7777777782",
        )

        self.category = StoreCategory.objects.create(
            college=self.college,
            name="Supplies",
            code="SUP",
        )
        self.item = StoreItem.objects.create(
            college=self.college,
            category=self.category,
            name="Notebook",
            code="NB001",
            unit="piece",
            price=Decimal('50.00'),
            stock_quantity=0,
            min_stock_level=5,
        )
        self.vendor = Vendor.objects.create(
            college=self.college,
            name="Vendor Co",
            phone="8888888888",
        )

        # Receive stock
        self.receive = StockReceive.objects.create(
            item=self.item,
            vendor=self.vendor,
            quantity=20,
            unit_price=Decimal('30.00'),
            total_amount=Decimal('600.00'),
            receive_date=date(2025, 6, 2),
        )

        # Sale on credit to student
        self.sale = StoreSale.objects.create(
            college=self.college,
            student=self.student,
            sale_date=date(2025, 6, 3),
            total_amount=Decimal('100.00'),
            payment_method='cash',
            payment_status='pending',
        )
        self.sale_item = SaleItem.objects.create(
            sale=self.sale,
            item=self.item,
            quantity=2,
            unit_price=Decimal('50.00'),
            total_price=Decimal('100.00'),
        )

        self.print_job = PrintJob.objects.create(
            college=self.college,
            teacher=self.teacher,
            job_name="Exam Papers",
            pages=10,
            copies=1,
            per_page_cost=Decimal('2.00'),
            total_amount=Decimal('0.00'),
            submission_date=date(2025, 6, 4),
            status='pending',
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(StoreCategory.objects.count(), 1)
        self.assertEqual(StoreItem.objects.count(), 1)
        self.assertEqual(Vendor.objects.count(), 1)
        self.assertEqual(StockReceive.objects.count(), 1)
        self.assertEqual(StoreSale.objects.count(), 1)
        self.assertEqual(SaleItem.objects.count(), 1)
        self.assertEqual(PrintJob.objects.count(), 1)

        # Stock adjustments: +20 received, -2 sold => 18 remaining
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_quantity, 18)

        # Credit entry created for pending payment
        self.assertGreaterEqual(StoreCredit.objects.count(), 1)
        credit = StoreCredit.objects.first()
        self.assertEqual(credit.amount, self.sale.total_amount)

        # Print job total recalculated
        self.print_job.refresh_from_db()
        self.assertEqual(self.print_job.total_amount, Decimal('20.00'))

        # __str__ calls
        str(self.category)
        str(self.item)
        str(self.vendor)
        str(self.receive)
        str(self.sale)
        str(self.sale_item)
        str(credit)
        str(self.print_job)
