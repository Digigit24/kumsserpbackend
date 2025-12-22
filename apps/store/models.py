"""
Store models for inventory, sales, and print jobs.
"""
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import CollegeScopedModel, AuditModel, College
from apps.students.models import Student
from apps.teachers.models import Teacher


class StoreCategory(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='store_categories',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Category name")
    code = models.CharField(max_length=20, help_text="Category code")
    description = models.TextField(null=True, blank=True, help_text="Description")

    class Meta:
        db_table = 'store_category'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
            models.Index(fields=['college', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class StoreItem(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='store_items',
        help_text="College reference"
    )
    category = models.ForeignKey(
        StoreCategory,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Category"
    )
    name = models.CharField(max_length=200, help_text="Item name")
    code = models.CharField(max_length=50, help_text="Item code")
    description = models.TextField(null=True, blank=True, help_text="Description")
    unit = models.CharField(max_length=20, help_text="Unit (piece/kg/ltr)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    stock_quantity = models.IntegerField(default=0, help_text="Stock quantity")
    min_stock_level = models.IntegerField(default=10, help_text="Minimum stock alert threshold")
    barcode = models.CharField(max_length=50, null=True, blank=True, help_text="Barcode")
    image = models.ImageField(upload_to='store_items/', null=True, blank=True, help_text="Item image")

    class Meta:
        db_table = 'store_item'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'category']),
            models.Index(fields=['college', 'code']),
            models.Index(fields=['barcode']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def adjust_stock(self, delta):
        self.stock_quantity = max(0, self.stock_quantity + delta)
        self.save(update_fields=['stock_quantity', 'updated_at'])

    def clean(self):
        if self.stock_quantity is not None and self.stock_quantity < 0:
            raise ValidationError("Stock quantity cannot be negative.")


class Vendor(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='vendors',
        help_text="College reference"
    )
    name = models.CharField(max_length=200, help_text="Vendor name")
    contact_person = models.CharField(max_length=100, null=True, blank=True, help_text="Contact person")
    email = models.EmailField(null=True, blank=True, help_text="Email")
    phone = models.CharField(max_length=20, help_text="Phone")
    address = models.TextField(null=True, blank=True, help_text="Address")
    gstin = models.CharField(max_length=15, null=True, blank=True, help_text="GSTIN")

    class Meta:
        db_table = 'vendor'
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class StockReceive(AuditModel):
    item = models.ForeignKey(
        StoreItem,
        on_delete=models.CASCADE,
        related_name='stock_receipts',
        help_text="Item"
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_receipts',
        help_text="Vendor"
    )
    quantity = models.IntegerField(help_text="Quantity received")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit price")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount")
    receive_date = models.DateField(help_text="Receive date")
    invoice_number = models.CharField(max_length=50, null=True, blank=True, help_text="Invoice number")
    invoice_file = models.FileField(upload_to='store_invoices/', null=True, blank=True, help_text="Invoice file")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")

    class Meta:
        db_table = 'stock_receive'
        indexes = [
            models.Index(fields=['item', 'vendor', 'receive_date']),
        ]

    def __str__(self):
        return f"Receive {self.quantity} of {self.item}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        if self.total_amount < 0:
            raise ValidationError("Total amount cannot be negative.")


class StoreSale(AuditModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='store_sales',
        help_text="College reference"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_sales',
        help_text="Student buyer"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_sales',
        help_text="Teacher buyer"
    )
    sale_date = models.DateField(help_text="Sale date")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount")
    payment_method = models.CharField(max_length=20, help_text="Payment method")
    payment_status = models.CharField(max_length=20, default='paid', help_text="Payment status")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")
    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_sales_made',
        help_text="Sold by user"
    )

    class Meta:
        db_table = 'store_sale'
        indexes = [
            models.Index(fields=['college', 'student', 'teacher', 'sale_date']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return f"Sale on {self.sale_date} ({self.total_amount})"

    def clean(self):
        if not self.student and not self.teacher:
            raise ValidationError("Sale must be associated with a student or teacher.")
        if self.student and self.teacher:
            raise ValidationError("Sale cannot be linked to both student and teacher.")


class SaleItem(AuditModel):
    sale = models.ForeignKey(
        StoreSale,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Sale"
    )
    item = models.ForeignKey(
        StoreItem,
        on_delete=models.CASCADE,
        related_name='sale_items',
        help_text="Item"
    )
    quantity = models.IntegerField(help_text="Quantity sold")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Unit price")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price")

    class Meta:
        db_table = 'sale_item'
        indexes = [
            models.Index(fields=['sale', 'item']),
        ]

    def __str__(self):
        return f"{self.item} x {self.quantity}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.unit_price < 0 or self.total_price < 0:
            raise ValidationError("Prices must be non-negative.")


class PrintJob(AuditModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='print_jobs',
        help_text="College reference"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='print_jobs',
        help_text="Teacher"
    )
    job_name = models.CharField(max_length=200, help_text="Job name")
    file = models.FileField(upload_to='print_jobs/', null=True, blank=True, help_text="File to print")
    pages = models.IntegerField(help_text="Number of pages")
    copies = models.IntegerField(default=1, help_text="Number of copies")
    paper_size = models.CharField(max_length=20, default='A4', help_text="Paper size")
    color_type = models.CharField(max_length=20, default='bw', help_text="Color type (bw/color)")
    per_page_cost = models.DecimalField(max_digits=6, decimal_places=2, help_text="Per page cost")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount")
    submission_date = models.DateField(help_text="Submission date")
    completion_date = models.DateField(null=True, blank=True, help_text="Completion date")
    status = models.CharField(max_length=20, default='pending', help_text="Status")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")

    class Meta:
        db_table = 'print_job'
        indexes = [
            models.Index(fields=['college', 'teacher', 'submission_date', 'status']),
        ]

    def __str__(self):
        return self.job_name

    def clean(self):
        if self.pages <= 0 or self.copies <= 0:
            raise ValidationError("Pages and copies must be positive.")


class StoreCredit(AuditModel):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='store_credits',
        help_text="Student"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Credit amount")
    transaction_type = models.CharField(max_length=20, help_text="Type (credit/debit)")
    date = models.DateField(help_text="Date")
    reference_type = models.CharField(max_length=50, null=True, blank=True, help_text="Reference type")
    reference_id = models.IntegerField(null=True, blank=True, help_text="Reference ID")
    reason = models.TextField(help_text="Reason")
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, help_text="Balance after transaction")

    class Meta:
        db_table = 'store_credit'
        indexes = [
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.transaction_type} {self.amount} for {self.student}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative.")
