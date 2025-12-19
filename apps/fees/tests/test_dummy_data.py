from datetime import date

from django.test import TestCase

from apps.core.models import College, AcademicYear
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program, AcademicSession
from apps.students.models import Student
from apps.fees.models import (
    FeeGroup,
    FeeType,
    FeeMaster,
    FeeStructure,
    FeeDiscount,
    StudentFeeDiscount,
    FeeCollection,
    FeeReceipt,
    FeeInstallment,
    FeeFine,
    FeeRefund,
    BankPayment,
    OnlinePayment,
    FeeReminder,
)


class FeesDummyDataTest(TestCase):
    """Build a dummy fee graph and verify relationships."""

    def setUp(self):
        self.college = College.objects.create(
            code="FEE",
            name="Fees College",
            short_name="FEE",
            email="info@fee.test",
            phone="9999999993",
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
        self.student_user = User.objects.create_user(
            username="student_fee",
            email="student_fee@fee.test",
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
            admission_number="ADM-FEE-001",
            admission_date=date(2025, 6, 1),
            admission_type="regular",
            registration_number="REG-FEE-001",
            program=self.program,
            current_class=None,
            current_section=None,
            academic_year=self.year,
            first_name="Stu",
            last_name="Dent",
            date_of_birth=date(2007, 1, 1),
            gender="male",
            email="student_fee@fee.test",
        )

        self.group = FeeGroup.objects.create(
            college=self.college,
            name="Tuition",
            code="TUI",
        )
        self.fee_type = FeeType.objects.create(
            college=self.college,
            fee_group=self.group,
            name="Semester Fee",
            code="SEM-FEE",
        )
        self.fee_master = FeeMaster.objects.create(
            college=self.college,
            program=self.program,
            academic_year=self.year,
            semester=1,
            fee_type=self.fee_type,
            amount=50000,
        )
        self.fee_structure = FeeStructure.objects.create(
            student=self.student,
            fee_master=self.fee_master,
            amount=50000,
            due_date=date(2025, 7, 1),
            balance=50000,
        )
        self.discount = FeeDiscount.objects.create(
            college=self.college,
            name="Merit",
            code="MERIT10",
            discount_type="percentage",
            percentage=10,
        )
        self.student_discount = StudentFeeDiscount.objects.create(
            student=self.student,
            discount=self.discount,
            applied_date=date(2025, 6, 15),
            remarks="Merit based",
        )
        self.collection = FeeCollection.objects.create(
            student=self.student,
            amount=20000,
            payment_method="cash",
            payment_date=date(2025, 6, 20),
            status="paid",
            transaction_id="TXN-FEE-001",
        )
        # FeeReceipt is created by signal, but ensure one exists for assertions
        self.receipt = FeeReceipt.objects.first() or FeeReceipt.objects.create(
            collection=self.collection,
            receipt_number="RCPT-MANUAL",
        )
        # Installment and reminder are auto-created on FeeStructure signal
        self.installment = FeeInstallment.objects.first()
        self.reminder = FeeReminder.objects.first()
        self.fine = FeeFine.objects.create(
            student=self.student,
            fee_structure=self.fee_structure,
            amount=500,
            reason="Late payment",
            fine_date=date(2025, 7, 5),
        )
        self.refund = FeeRefund.objects.create(
            student=self.student,
            amount=1000,
            reason="Overpayment",
            refund_date=date(2025, 8, 1),
            payment_method="bank",
            transaction_id="RFND-001",
        )
        self.bank_payment = BankPayment.objects.create(
            collection=self.collection,
            bank_name="Test Bank",
            branch="Main",
            cheque_dd_number="CHQ123",
            cheque_dd_date=date(2025, 6, 20),
            transaction_id="BANK-TXN-1",
        )
        self.online_payment = OnlinePayment.objects.create(
            collection=self.collection,
            gateway="Razorpay",
            transaction_id="ONL-TXN-1",
            order_id="ORDER-1",
            payment_mode="upi",
            status="success",
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        def count(model):
            manager = model.objects
            return manager.all_colleges().count() if hasattr(manager, "all_colleges") else manager.count()

        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(count(AcademicYear), 1)
        self.assertEqual(count(Program), 1)
        self.assertEqual(count(FeeGroup), 1)
        self.assertEqual(count(FeeType), 1)
        self.assertEqual(count(FeeMaster), 1)
        self.assertEqual(FeeStructure.objects.count(), 1)
        self.assertEqual(count(FeeDiscount), 1)
        self.assertEqual(StudentFeeDiscount.objects.count(), 1)
        self.assertEqual(FeeCollection.objects.count(), 1)
        self.assertGreaterEqual(FeeReceipt.objects.count(), 1)
        self.assertGreaterEqual(FeeInstallment.objects.count(), 1)
        self.assertEqual(FeeFine.objects.count(), 1)
        self.assertEqual(FeeRefund.objects.count(), 1)
        self.assertEqual(BankPayment.objects.count(), 1)
        self.assertEqual(OnlinePayment.objects.count(), 1)
        self.assertGreaterEqual(FeeReminder.objects.count(), 1)

        # Relationship sanity
        self.assertEqual(self.fee_type.fee_group, self.group)
        self.assertEqual(self.fee_master.fee_type, self.fee_type)
        self.assertEqual(self.fee_structure.student, self.student)
        self.assertEqual(self.student_discount.discount, self.discount)
        self.assertEqual(self.collection.student, self.student)
        self.assertEqual(self.receipt.collection, self.collection)
        if self.installment:
            self.assertEqual(self.installment.fee_structure, self.fee_structure)
        if self.reminder:
            self.assertEqual(self.reminder.fee_structure, self.fee_structure)

        # __str__ calls
        str(self.group)
        str(self.fee_type)
        str(self.fee_master)
        str(self.fee_structure)
        str(self.discount)
        str(self.student_discount)
        str(self.collection)
        str(self.receipt)
        if self.installment:
            str(self.installment)
        str(self.fine)
        str(self.refund)
        str(self.bank_payment)
        str(self.online_payment)
        if self.reminder:
            str(self.reminder)
