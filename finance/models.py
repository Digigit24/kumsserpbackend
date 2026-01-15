from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class AppIncome(models.Model):
    """Income tracking per app per month"""
    APP_CHOICES = [
        ('fees', 'Fees'),
        ('library', 'Library'),
        ('hostel', 'Hostel'),
        ('store', 'Store'),
    ]

    app_name = models.CharField(max_length=50, choices=APP_CHOICES)
    month = models.DateField(help_text="First day of the month")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    transaction_count = models.IntegerField(default=0)
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_app_income'
        unique_together = ['app_name', 'month']
        ordering = ['-month', 'app_name']
        indexes = [
            models.Index(fields=['app_name', 'month']),
            models.Index(fields=['month']),
        ]

    def __str__(self):
        return f"{self.app_name} - {self.month.strftime('%Y-%m')}: ₹{self.amount}"


class AppExpense(models.Model):
    """Expense tracking per app per month"""
    APP_CHOICES = [
        ('fees', 'Fees'),
        ('hr', 'HR'),
        ('store', 'Store'),
        ('other', 'Other'),
    ]

    app_name = models.CharField(max_length=50, choices=APP_CHOICES)
    month = models.DateField(help_text="First day of the month")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    transaction_count = models.IntegerField(default=0)
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_app_expense'
        unique_together = ['app_name', 'month']
        ordering = ['-month', 'app_name']
        indexes = [
            models.Index(fields=['app_name', 'month']),
            models.Index(fields=['month']),
        ]

    def __str__(self):
        return f"{self.app_name} - {self.month.strftime('%Y-%m')}: ₹{self.amount}"


class AppTotal(models.Model):
    """Net total per app per month (income - expense)"""
    APP_CHOICES = [
        ('fees', 'Fees'),
        ('library', 'Library'),
        ('hostel', 'Hostel'),
        ('hr', 'HR'),
        ('store', 'Store'),
        ('other', 'Other'),
    ]

    app_name = models.CharField(max_length=50, choices=APP_CHOICES)
    month = models.DateField(help_text="First day of the month")
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_app_total'
        unique_together = ['app_name', 'month']
        ordering = ['-month', 'app_name']
        indexes = [
            models.Index(fields=['app_name', 'month']),
            models.Index(fields=['month']),
        ]

    def calculate_net(self):
        """Calculate net total"""
        self.net_total = self.income - self.expense
        return self.net_total

    def __str__(self):
        return f"{self.app_name} - {self.month.strftime('%Y-%m')}: ₹{self.net_total}"


class FinanceTotal(models.Model):
    """Overall finance totals per month"""
    month = models.DateField(unique=True, help_text="First day of the month")
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_total'
        ordering = ['-month']
        indexes = [
            models.Index(fields=['month']),
        ]

    def calculate_net(self):
        """Calculate net total"""
        self.net_total = self.total_income - self.total_expense
        return self.net_total

    def __str__(self):
        return f"{self.month.strftime('%Y-%m')}: ₹{self.net_total}"


class OtherExpense(models.Model):
    """Additional expenses not covered by other apps"""
    CATEGORY_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('utilities', 'Utilities'),
        ('supplies', 'Supplies'),
        ('marketing', 'Marketing'),
        ('travel', 'Travel'),
        ('miscellaneous', 'Miscellaneous'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    date = models.DateField()
    receipt = models.FileField(upload_to='finance/receipts/%Y/%m/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='other_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_other_expense'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.date})"


class FinanceTransaction(models.Model):
    """Unified transaction log for all finance activities"""
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    APP_CHOICES = [
        ('fees', 'Fees'),
        ('library', 'Library'),
        ('hostel', 'Hostel'),
        ('hr', 'HR'),
        ('store', 'Store'),
        ('other', 'Other'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
    ]

    app = models.CharField(max_length=50, choices=APP_CHOICES)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=500)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_id = models.IntegerField(null=True, blank=True, help_text="ID from source app")
    reference_model = models.CharField(max_length=100, blank=True, help_text="Source model name")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_transaction'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['app', 'type']),
            models.Index(fields=['date']),
            models.Index(fields=['reference_model', 'reference_id']),
        ]

    def __str__(self):
        return f"{self.app} - {self.type} - ₹{self.amount} ({self.date})"
