"""
HR models for leave and payroll management.
"""
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import CollegeScopedModel, AuditModel, College, AcademicYear
from apps.teachers.models import Teacher


class LeaveType(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='leave_types',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Leave type")
    code = models.CharField(max_length=20, help_text="Code")
    max_days_per_year = models.IntegerField(help_text="Max days per year")
    is_paid = models.BooleanField(default=True, help_text="Paid leave")
    description = models.TextField(null=True, blank=True, help_text="Description")

    class Meta:
        db_table = 'leave_type'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
            models.Index(fields=['college', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class LeaveApplication(AuditModel):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='leave_applications',
        help_text="Teacher"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='leave_applications',
        help_text="Leave type"
    )
    from_date = models.DateField(help_text="From date")
    to_date = models.DateField(help_text="To date")
    total_days = models.IntegerField(help_text="Total days")
    reason = models.TextField(help_text="Reason")
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True, help_text="Attachment")
    status = models.CharField(max_length=20, default='pending', help_text="Status")
    applied_date = models.DateField(auto_now_add=True, help_text="Applied date")

    class Meta:
        db_table = 'leave_application'
        indexes = [
            models.Index(fields=['teacher', 'leave_type', 'from_date', 'status']),
        ]

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.leave_type} ({self.from_date} to {self.to_date})"

    def clean(self):
        if self.to_date and self.from_date and self.to_date < self.from_date:
            raise ValidationError("To date cannot be before from date.")
        if self.total_days <= 0:
            raise ValidationError("Total days must be positive.")


class LeaveApproval(AuditModel):
    application = models.ForeignKey(
        LeaveApplication,
        on_delete=models.CASCADE,
        related_name='approvals',
        help_text="Leave application"
    )
    status = models.CharField(max_length=20, help_text="Status")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_approvals',
        help_text="Approved by"
    )
    approval_date = models.DateField(help_text="Approval date")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")

    class Meta:
        db_table = 'leave_approval'
        indexes = [
            models.Index(fields=['application', 'approved_by']),
        ]

    def __str__(self):
        return f"Approval for {self.application} ({self.status})"


class LeaveBalance(AuditModel):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='leave_balances',
        help_text="Teacher"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='leave_balances',
        help_text="Leave type"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='leave_balances',
        help_text="Academic year"
    )
    total_days = models.IntegerField(help_text="Total days")
    used_days = models.IntegerField(default=0, help_text="Used days")
    balance_days = models.IntegerField(help_text="Balance days")

    class Meta:
        db_table = 'leave_balance'
        unique_together = ['teacher', 'leave_type', 'academic_year']
        indexes = [
            models.Index(fields=['teacher', 'leave_type', 'academic_year']),
        ]

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.leave_type} ({self.balance_days} days left)"

    def clean(self):
        if self.total_days < 0 or self.used_days < 0 or self.balance_days < 0:
            raise ValidationError("Days cannot be negative.")


class SalaryStructure(AuditModel):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='salary_structures',
        help_text="Teacher"
    )
    effective_from = models.DateField(help_text="Effective from")
    effective_to = models.DateField(null=True, blank=True, help_text="Effective to")
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, help_text="Basic salary")
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="HRA")
    da = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="DA")
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Other allowances")
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, help_text="Gross salary")
    is_current = models.BooleanField(default=True, help_text="Current structure")

    class Meta:
        db_table = 'salary_structure'
        indexes = [
            models.Index(fields=['teacher', 'effective_from', 'is_current']),
        ]

    def __str__(self):
        return f"Salary Structure - {self.teacher.get_full_name()} ({self.effective_from})"

    def clean(self):
        if self.effective_to and self.effective_to < self.effective_from:
            raise ValidationError("Effective to date cannot be before effective from date.")


class SalaryComponent(AuditModel):
    structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.CASCADE,
        related_name='components',
        help_text="Salary structure"
    )
    component_name = models.CharField(max_length=100, help_text="Component name")
    component_type = models.CharField(max_length=20, help_text="Type (allowance/deduction)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount")
    is_taxable = models.BooleanField(default=True, help_text="Taxable")

    class Meta:
        db_table = 'salary_component'
        indexes = [
            models.Index(fields=['structure']),
        ]

    def __str__(self):
        return f"{self.component_name} ({self.component_type})"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")


class Deduction(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='deductions',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Deduction name")
    code = models.CharField(max_length=20, help_text="Code")
    deduction_type = models.CharField(max_length=20, help_text="Type (fixed/percentage)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Fixed amount")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Percentage")

    class Meta:
        db_table = 'deduction'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Payroll(AuditModel):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='payrolls',
        help_text="Teacher"
    )
    month = models.IntegerField(help_text="Month (1-12)")
    year = models.IntegerField(help_text="Year")
    salary_structure = models.ForeignKey(
        SalaryStructure,
        on_delete=models.CASCADE,
        related_name='payrolls',
        help_text="Salary structure"
    )
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, help_text="Gross salary")
    total_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total allowances")
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total deductions")
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, help_text="Net salary")
    payment_date = models.DateField(null=True, blank=True, help_text="Payment date")
    payment_method = models.CharField(max_length=20, null=True, blank=True, help_text="Payment method")
    status = models.CharField(max_length=20, default='pending', help_text="Status")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")

    class Meta:
        db_table = 'payroll'
        unique_together = ['teacher', 'month', 'year']
        indexes = [
            models.Index(fields=['teacher', 'month', 'year']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payroll {self.month}/{self.year} - {self.teacher.get_full_name()}"

    def clean(self):
        if self.month < 1 or self.month > 12:
            raise ValidationError("Month must be between 1 and 12.")


class PayrollItem(AuditModel):
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Payroll"
    )
    component_name = models.CharField(max_length=100, help_text="Component name")
    component_type = models.CharField(max_length=20, help_text="Type (allowance/deduction)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount")

    class Meta:
        db_table = 'payroll_item'
        indexes = [
            models.Index(fields=['payroll']),
        ]

    def __str__(self):
        return f"{self.component_name} ({self.amount})"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")


class Payslip(AuditModel):
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name='payslips',
        help_text="Payroll"
    )
    slip_number = models.CharField(max_length=50, unique=True, help_text="Slip number")
    slip_file = models.FileField(upload_to='payslips/', null=True, blank=True, help_text="Slip PDF")
    issue_date = models.DateField(help_text="Issue date")

    class Meta:
        db_table = 'payslip'
        indexes = [
            models.Index(fields=['payroll', 'slip_number']),
        ]

    def __str__(self):
        return f"Payslip {self.slip_number}"

    def clean(self):
        if self.issue_date > date.today():
            raise ValidationError("Issue date cannot be in the future.")
