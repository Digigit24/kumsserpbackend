from django.db import models
from django.conf import settings

from apps.core.models import CollegeScopedModel, AuditModel, College, AcademicYear
from apps.academic.models import Program, Class, Section, SubjectAssignment, ClassTime
from apps.students.models import Student


class FeeGroup(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='fee_groups')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'fee_group'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class FeeType(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='fee_types')
    fee_group = models.ForeignKey(FeeGroup, on_delete=models.CASCADE, related_name='fee_types')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'fee_type'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'fee_group', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class FeeMaster(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='fee_masters')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='fee_masters')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_masters')
    semester = models.IntegerField()
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, related_name='fee_masters')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'fee_master'
        unique_together = ['college', 'program', 'academic_year', 'semester', 'fee_type']
        indexes = [
            models.Index(fields=['college', 'program', 'academic_year', 'semester']),
        ]

    def __str__(self):
        return f"{self.program.short_name} Sem {self.semester} - {self.fee_type.code}"


class FeeStructure(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_structures')
    fee_master = models.ForeignKey(FeeMaster, on_delete=models.CASCADE, related_name='fee_structures')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'fee_structure'
        indexes = [
            models.Index(fields=['student', 'fee_master', 'due_date', 'is_paid']),
        ]

    def __str__(self):
        return f"{self.student} - {self.fee_master} - {self.amount}"


class FeeDiscount(CollegeScopedModel):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='fee_discounts')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    discount_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    criteria = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'fee_discount'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class StudentFeeDiscount(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_discounts')
    discount = models.ForeignKey(FeeDiscount, on_delete=models.CASCADE, related_name='student_discounts')
    applied_date = models.DateField()
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'student_fee_discount'
        indexes = [
            models.Index(fields=['student', 'discount']),
        ]

    def __str__(self):
        return f"{self.student} - {self.discount}"


class FeeCollection(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_collections')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20)
    payment_date = models.DateField()
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    collected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='fees_collected')

    class Meta:
        db_table = 'fee_collection'
        indexes = [
            models.Index(fields=['student', 'payment_date', 'status', 'transaction_id']),
        ]

    def __str__(self):
        return f"{self.student} - {self.amount} on {self.payment_date}"


class FeeReceipt(AuditModel):
    collection = models.ForeignKey(FeeCollection, on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_file = models.FileField(upload_to='fee_receipts/', null=True, blank=True)

    class Meta:
        db_table = 'fee_receipt'
        indexes = [
            models.Index(fields=['collection', 'receipt_number']),
        ]

    def __str__(self):
        return f"Receipt {self.receipt_number}"


class FeeInstallment(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_installments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'fee_installment'
        indexes = [
            models.Index(fields=['student', 'fee_structure', 'due_date']),
        ]

    def __str__(self):
        return f"Installment {self.installment_number} - {self.student}"


class FeeFine(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_fines')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True, related_name='fines')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    fine_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'fee_fine'
        indexes = [
            models.Index(fields=['student', 'fine_date', 'is_paid']),
        ]

    def __str__(self):
        return f"Fine {self.amount} for {self.student}"


class FeeRefund(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    refund_date = models.DateField()
    payment_method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='fee_refunds_processed')

    class Meta:
        db_table = 'fee_refund'
        indexes = [
            models.Index(fields=['student', 'refund_date']),
        ]

    def __str__(self):
        return f"Refund {self.amount} to {self.student}"


class BankPayment(AuditModel):
    collection = models.ForeignKey(FeeCollection, on_delete=models.CASCADE, related_name='bank_payments')
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, null=True, blank=True)
    cheque_dd_number = models.CharField(max_length=50, null=True, blank=True)
    cheque_dd_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'bank_payment'
        indexes = [
            models.Index(fields=['collection', 'transaction_id']),
        ]

    def __str__(self):
        return f"Bank Payment - {self.collection}"


class OnlinePayment(AuditModel):
    collection = models.ForeignKey(FeeCollection, on_delete=models.CASCADE, related_name='online_payments')
    gateway = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    payment_mode = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20)
    response_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'online_payment'
        indexes = [
            models.Index(fields=['collection', 'transaction_id', 'status']),
        ]

    def __str__(self):
        return f"Online Payment {self.transaction_id}"


class FeeReminder(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_reminders')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='reminders')
    reminder_date = models.DateField()
    reminder_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    message = models.TextField()

    class Meta:
        db_table = 'fee_reminder'
        indexes = [
            models.Index(fields=['student', 'reminder_date', 'status']),
        ]

    def __str__(self):
        return f"Reminder for {self.student} on {self.reminder_date}"
