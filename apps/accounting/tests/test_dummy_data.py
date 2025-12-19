from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.core.models import College
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.accounting.models import (
    IncomeCategory,
    ExpenseCategory,
    Income,
    Expense,
    Account,
    Voucher,
    FinancialYear,
    AccountTransaction,
)


class AccountingDummyDataTest(TestCase):
    """Build a dummy accounting graph and verify relationships."""

    def setUp(self):
        self.college = College.objects.create(
            code="ACC",
            name="Accounting College",
            short_name="ACC",
            email="info@acc.test",
            phone="9999999994",
            address_line1="123 Street",
            city="City",
            state="State",
            pincode="000000",
            country="Testland",
        )
        set_current_college_id(self.college.id)

        self.user = User.objects.create_user(
            username="acc_user",
            email="acc@acc.test",
            password="dummy-pass",
            first_name="Acc",
            last_name="User",
            college=self.college,
            user_type=UserType.COLLEGE_ADMIN,
            is_active=True,
        )

        self.fin_year = FinancialYear.objects.create(
            college=self.college,
            year="2025-2026",
            start_date=date(2025, 4, 1),
            end_date=date(2026, 3, 31),
            is_current=True,
            created_by=self.user,
            updated_by=self.user,
        )
        self.account = Account.objects.create(
            college=self.college,
            account_name="Primary",
            account_number="ACC-001",
            bank_name="Test Bank",
            balance=Decimal("1000.00"),
            created_by=self.user,
            updated_by=self.user,
        )
        self.income_cat = IncomeCategory.objects.create(
            college=self.college,
            name="Donations",
            code="DON",
            created_by=self.user,
            updated_by=self.user,
        )
        self.expense_cat = ExpenseCategory.objects.create(
            college=self.college,
            name="Utilities",
            code="UTL",
            created_by=self.user,
            updated_by=self.user,
        )
        self.income = Income.objects.create(
            college=self.college,
            category=self.income_cat,
            amount=Decimal("500.00"),
            date=date(2025, 5, 1),
            description="Donation",
            payment_method="cash",
            created_by=self.user,
            updated_by=self.user,
        )
        self.expense = Expense.objects.create(
            college=self.college,
            category=self.expense_cat,
            amount=Decimal("200.00"),
            date=date(2025, 5, 2),
            description="Electricity bill",
            payment_method="bank",
            paid_to="Power Co",
            created_by=self.user,
            updated_by=self.user,
        )
        # Signals should create vouchers and account transactions; ensure one account transaction exists.
        self.voucher_income = Voucher.objects.filter(voucher_type='receipt').first()
        self.voucher_expense = Voucher.objects.filter(voucher_type='payment').first()
        self.transactions = AccountTransaction.objects.all()

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        self.assertEqual(College.objects.count(), 1)
        self.assertEqual(FinancialYear.objects.count(), 1)
        self.assertGreaterEqual(Account.objects.count(), 1)
        self.assertEqual(IncomeCategory.objects.count(), 1)
        self.assertEqual(ExpenseCategory.objects.count(), 1)
        self.assertEqual(Income.objects.count(), 1)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertGreaterEqual(Voucher.objects.count(), 2)
        self.assertGreaterEqual(AccountTransaction.objects.count(), 2)

        # Relationships and balances
        self.assertEqual(self.income.category, self.income_cat)
        self.assertEqual(self.expense.category, self.expense_cat)
        self.assertIsNotNone(self.voucher_income)
        self.assertIsNotNone(self.voucher_expense)

        # __str__ calls
        str(self.fin_year)
        str(self.account)
        str(self.income)
        str(self.expense)
        str(self.voucher_income)
        str(self.transactions.first())
