from django.db import models
from django.conf import settings

from apps.core.models import CollegeScopedModel, AuditModel, College


class IncomeCategory(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='income_categories')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'income_category'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class ExpenseCategory(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'expense_category'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Account(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='accounts')
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'account'
        indexes = [
            models.Index(fields=['college', 'account_number']),
        ]

    def __str__(self):
        return f"{self.account_name} ({self.account_number})"


class FinancialYear(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='financial_years')
    year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = 'financial_year'
        unique_together = ['college', 'year']
        indexes = [
            models.Index(fields=['college', 'year', 'is_current']),
        ]

    def __str__(self):
        return self.year


class Income(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='income')
    category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE, related_name='income')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    invoice_file = models.FileField(upload_to='income_invoices/', null=True, blank=True)
    payment_method = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'income'
        indexes = [
            models.Index(fields=['college', 'category', 'date']),
        ]

    def __str__(self):
        return f"Income {self.amount} on {self.date}"


class Expense(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    receipt_file = models.FileField(upload_to='expense_receipts/', null=True, blank=True)
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    paid_to = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'expense'
        indexes = [
            models.Index(fields=['college', 'category', 'date']),
        ]

    def __str__(self):
        return f"Expense {self.amount} on {self.date}"


class Voucher(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='vouchers')
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='vouchers')
    voucher_number = models.CharField(max_length=50, unique=True)
    voucher_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField()

    class Meta:
        db_table = 'voucher'
        indexes = [
            models.Index(fields=['college', 'voucher_number', 'date']),
        ]

    def __str__(self):
        return f"{self.voucher_number} - {self.voucher_type}"


class AccountTransaction(AuditModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    reference_type = models.CharField(max_length=50, null=True, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'account_transaction'
        indexes = [
            models.Index(fields=['account', 'date', 'transaction_type']),
        ]

    def __str__(self):
        return f"{self.transaction_type} {self.amount} on {self.date}"
