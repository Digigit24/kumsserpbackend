from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.core.models import College, AcademicYear
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.academic.models import Faculty, Program
from apps.teachers.models import Teacher
from apps.attendance.models import StaffAttendance
from apps.hr.models import (
    LeaveType,
    LeaveApplication,
    LeaveApproval,
    LeaveBalance,
    SalaryStructure,
    SalaryComponent,
    Deduction,
    Payroll,
    PayrollItem,
    Payslip,
)


class HRDummyDataTest(TestCase):
    """Build a dummy HR graph and verify relationships and signals."""

    def setUp(self):
        self.college = College.objects.create(
            code="HR",
            name="HR College",
            short_name="HR",
            email="info@hr.test",
            phone="9999999996",
            address_line1="123 HR St",
            city="City",
            state="State",
            pincode="000003",
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
            code="HRF",
            name="HR Faculty",
            short_name="HRF",
            display_order=1,
        )
        self.program = Program.objects.create(
            college=self.college,
            faculty=self.faculty,
            code="HRP",
            name="HR Program",
            short_name="HRP",
            program_type="pg",
            duration=2,
            duration_type="year",
            total_credits=80,
            display_order=1,
        )

        self.teacher_user = User.objects.create_user(
            username="teacher_hr",
            email="teacher@hr.test",
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
            employee_id="EMP-HR-001",
            joining_date=date(2025, 6, 1),
            faculty=self.faculty,
            first_name="Tea",
            last_name="Cher",
            date_of_birth=date(1990, 1, 1),
            gender="male",
            email="teacher@hr.test",
            phone="7777777783",
        )

        self.leave_type = LeaveType.objects.create(
            college=self.college,
            name="Casual Leave",
            code="CL",
            max_days_per_year=10,
        )

        self.leave_application = LeaveApplication.objects.create(
            teacher=self.teacher,
            leave_type=self.leave_type,
            from_date=date(2025, 6, 10),
            to_date=date(2025, 6, 11),
            total_days=2,
            reason="Personal work",
            status="pending",
        )
        # Approve leave to trigger balance update and attendance creation
        self.leave_approval = LeaveApproval.objects.create(
            application=self.leave_application,
            status='approved',
            approved_by=self.teacher_user,
            approval_date=date(2025, 6, 5),
        )

        self.salary_structure = SalaryStructure.objects.create(
            teacher=self.teacher,
            effective_from=date(2025, 6, 1),
            basic_salary=Decimal('40000.00'),
            hra=Decimal('10000.00'),
            da=Decimal('5000.00'),
            other_allowances=Decimal('2000.00'),
            gross_salary=Decimal('57000.00'),
            is_current=True,
        )
        self.allowance = SalaryComponent.objects.create(
            structure=self.salary_structure,
            component_name="Bonus",
            component_type="allowance",
            amount=Decimal('5000.00'),
            is_taxable=True,
        )
        self.deduction = SalaryComponent.objects.create(
            structure=self.salary_structure,
            component_name="Tax",
            component_type="deduction",
            amount=Decimal('1000.00'),
            is_taxable=True,
        )
        self.deduction_master = Deduction.objects.create(
            college=self.college,
            name="Professional Tax",
            code="PTX",
            deduction_type="fixed",
            amount=Decimal('200.00'),
        )

        self.payroll = Payroll.objects.create(
            teacher=self.teacher,
            month=6,
            year=2025,
            salary_structure=self.salary_structure,
            gross_salary=self.salary_structure.gross_salary,
            total_allowances=Decimal('0.00'),
            total_deductions=Decimal('0.00'),
            net_salary=Decimal('0.00'),
            status='processed',
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(LeaveType.objects.count(), 1)
        self.assertEqual(LeaveApplication.objects.count(), 1)
        self.assertEqual(LeaveApproval.objects.count(), 2)  # initial + approved
        self.assertEqual(SalaryStructure.objects.count(), 1)
        self.assertEqual(SalaryComponent.objects.count(), 2)
        self.assertEqual(Deduction.objects.count(), 1)
        self.assertEqual(Payroll.objects.count(), 1)

        # Leave balance and attendance updates
        balance = LeaveBalance.objects.first()
        self.assertIsNotNone(balance)
        self.assertEqual(balance.used_days, 2)
        self.assertEqual(balance.balance_days, 8)
        attendance_entries = StaffAttendance.objects.filter(teacher=self.teacher, status='on_leave')
        self.assertEqual(attendance_entries.count(), 2)

        # Payroll processing: items and payslip
        self.assertEqual(PayrollItem.objects.count(), 2)
        self.assertEqual(self.payroll.total_allowances, Decimal('5000.00'))
        self.assertEqual(self.payroll.total_deductions, Decimal('1000.00'))
        self.assertEqual(self.payroll.net_salary, Decimal('61000.00'))
        self.assertEqual(Payslip.objects.count(), 1)

        # __str__ calls
        str(self.leave_type)
        str(self.leave_application)
        str(balance)
        str(self.salary_structure)
        str(self.allowance)
        str(self.deduction_master)
        str(self.payroll)
