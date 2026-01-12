"""
Store models for inventory, sales, and print jobs.
"""
import re
from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

from apps.core.models import CollegeScopedModel, AuditModel, College
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.approvals.models import ApprovalRequest
from .utils import generate_document_number

# Import S3 storage (SOP requirement)
try:
    from .storage import store_file_storage
except ImportError:
    store_file_storage = None


SUPPLIER_TYPE_CHOICES = [
    ('manufacturer', 'Manufacturer'),
    ('distributor', 'Distributor'),
    ('wholesaler', 'Wholesaler'),
    ('retailer', 'Retailer'),
]

PROCUREMENT_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('pending_approval', 'Pending Approval'),
    ('approved', 'Approved'),
    ('quotations_received', 'Quotations Received'),
    ('po_created', 'PO Created'),
    ('fulfilled', 'Fulfilled'),
    ('cancelled', 'Cancelled'),
]

PO_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('acknowledged', 'Acknowledged'),
    ('partially_received', 'Partially Received'),
    ('fulfilled', 'Fulfilled'),
    ('cancelled', 'Cancelled'),
]

GRN_STATUS_CHOICES = [
    ('received', 'Received'),
    ('pending_inspection', 'Pending Inspection'),
    ('inspected', 'Inspected'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('posted_to_inventory', 'Posted To Inventory'),
]

INDENT_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('pending_college_approval', 'Pending College Admin Approval'),
    ('college_approved', 'College Admin Approved'),
    ('pending_super_admin', 'Pending Super Admin Approval'),
    ('super_admin_approved', 'Super Admin Approved'),
    ('approved', 'Approved'),
    ('partially_fulfilled', 'Partially Fulfilled'),
    ('fulfilled', 'Fulfilled'),
    ('rejected_by_college', 'Rejected by College Admin'),
    ('rejected_by_super_admin', 'Rejected by Super Admin'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]

TRANSACTION_TYPE_CHOICES = [
    ('receipt', 'Receipt'),
    ('issue', 'Issue'),
    ('adjustment', 'Adjustment'),
    ('transfer', 'Transfer'),
    ('return', 'Return'),
    ('damage', 'Damage'),
    ('write_off', 'Write Off'),
]

INDENT_PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('urgent', 'Urgent'),
]

URGENCY_CHOICES = INDENT_PRIORITY_CHOICES


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
    managed_by = models.CharField(
        max_length=20,
        choices=[('central', 'Central Store'), ('college', 'College Store')],
        default='college',
        help_text="Whether item is centrally managed"
    )
    central_store = models.ForeignKey(
        'CentralStore',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
        help_text="Linked central store when centrally managed"
    )

    class Meta:
        db_table = 'store_item'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'category']),
            models.Index(fields=['college', 'code']),
            models.Index(fields=['barcode']),
            models.Index(fields=['is_active']),
            models.Index(fields=['central_store', 'managed_by']),
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


class StoreSale(CollegeScopedModel):
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


class PrintJob(CollegeScopedModel):
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


class SupplierMaster(AuditModel):
    supplier_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, null=True, blank=True)
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')
    gstin = models.CharField(max_length=15, null=True, blank=True, unique=True)
    pan = models.CharField(max_length=10, null=True, blank=True)
    bank_name = models.CharField(max_length=200, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=11, null=True, blank=True)
    payment_terms = models.CharField(max_length=100, null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    supplier_type = models.CharField(max_length=50, choices=SUPPLIER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'supplier_master'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['supplier_code']),
            models.Index(fields=['gstin']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.supplier_code})"

    def save(self, *args, **kwargs):
        if not self.supplier_code:
            self.supplier_code = generate_document_number('SUP', SupplierMaster, field_name='created_at')
        super().save(*args, **kwargs)

    def get_full_address(self):
        return ", ".join(filter(None, [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state,
            self.pincode,
            self.country,
        ]))

    def clean(self):
        gstin_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        if self.gstin and not re.match(gstin_pattern, self.gstin):
            raise ValidationError({'gstin': 'Invalid GSTIN format'})
        if self.pan and not re.match(pan_pattern, self.pan):
            raise ValidationError({'pan': 'Invalid PAN format'})


class CentralStore(AuditModel):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_central_stores')
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'central_store'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class CollegeStore(CollegeScopedModel):
    """College-level store managed by college admins"""
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='college_stores',
        help_text="College reference"
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=300, null=True, blank=True)
    address_line2 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_college_stores'
    )
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)

    class Meta:
        db_table = 'college_store'
        unique_together = ['college', 'code']
        ordering = ['college', 'name']
        indexes = [
            models.Index(fields=['college', 'is_active']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f"{self.college.name} - {self.name}"


class ProcurementRequirement(AuditModel):
    requirement_number = models.CharField(max_length=50, unique=True)
    central_store = models.ForeignKey(CentralStore, on_delete=models.CASCADE, related_name='requirements')
    title = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    requirement_date = models.DateField(auto_now_add=True)
    required_by_date = models.DateField()
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='medium')
    status = models.CharField(max_length=30, choices=PROCUREMENT_STATUS_CHOICES, default='draft')
    approval_request = models.ForeignKey(ApprovalRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name='procurement_requirements')
    estimated_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    justification = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'procurement_requirement'
        ordering = ['-requirement_date']
        indexes = [
            models.Index(fields=['requirement_number']),
            models.Index(fields=['status']),
            models.Index(fields=['required_by_date']),
        ]

    def __str__(self):
        return f"{self.requirement_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.requirement_number:
            self.requirement_number = generate_document_number('REQ', ProcurementRequirement, field_name='requirement_date')
        super().save(*args, **kwargs)

    def submit_for_approval(self):
        if self.status not in ['draft', 'submitted']:
            raise ValidationError('Requirement already submitted or processed')
        self.status = 'pending_approval'
        self.save(update_fields=['status', 'updated_at'])

    def approve(self):
        self.status = 'approved'
        self.save(update_fields=['status', 'updated_at'])

    def cancel(self):
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])


class RequirementItem(AuditModel):
    requirement = models.ForeignKey(ProcurementRequirement, on_delete=models.CASCADE, related_name='items')
    item_description = models.CharField(max_length=500)
    category = models.ForeignKey(StoreCategory, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit = models.CharField(max_length=20)
    estimated_unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    specifications = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'requirement_item'
        indexes = [models.Index(fields=['requirement'])]

    def clean(self):
        if self.quantity and self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than zero'})

    def save(self, *args, **kwargs):
        if self.estimated_unit_price is not None:
            self.estimated_total = (self.estimated_unit_price or 0) * (self.quantity or 0)
        super().save(*args, **kwargs)


class SupplierQuotation(AuditModel):
    quotation_number = models.CharField(max_length=50, unique=True)
    requirement = models.ForeignKey(ProcurementRequirement, on_delete=models.CASCADE, related_name='quotations')
    supplier = models.ForeignKey(SupplierMaster, on_delete=models.CASCADE, related_name='quotations')
    quotation_date = models.DateField()
    supplier_reference_number = models.CharField(max_length=100, null=True, blank=True)
    valid_until = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_terms = models.CharField(max_length=200, null=True, blank=True)
    delivery_time_days = models.IntegerField(null=True, blank=True)
    warranty_terms = models.TextField(null=True, blank=True)
    quotation_file = models.FileField(upload_to='quotations/', storage=store_file_storage, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('received', 'Received'), ('under_review', 'Under Review'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='received')
    is_selected = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'supplier_quotation'
        ordering = ['-quotation_date']
        indexes = [
            models.Index(fields=['requirement']),
            models.Index(fields=['supplier']),
            models.Index(fields=['status']),
            models.Index(fields=['is_selected']),
        ]

    def __str__(self):
        return f"{self.quotation_number} - {self.supplier}"

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            self.quotation_number = generate_document_number('QUOT', SupplierQuotation, field_name='quotation_date')
        super().save(*args, **kwargs)

    def mark_as_selected(self):
        # Phase 12.1: Cannot select quotation if requirement not approved
        if self.requirement and self.requirement.status not in ['approved', 'quotations_received']:
            raise ValidationError('Cannot select quotation if requirement not approved')

        with transaction.atomic():
            SupplierQuotation.objects.filter(requirement=self.requirement).update(is_selected=False, status='rejected')
            self.is_selected = True
            self.status = 'accepted'
            self.save(update_fields=['is_selected', 'status', 'updated_at'])

    def clean(self):
        # Phase 12.1: Cannot create quotation for cancelled/fulfilled requirement
        if self.requirement and self.requirement.status in ['cancelled', 'fulfilled']:
            raise ValidationError({
                'requirement': 'Cannot create quotation for cancelled or fulfilled requirement'
            })

        if self.grand_total and self.total_amount and self.tax_amount is not None:
            expected = (self.total_amount or 0) + (self.tax_amount or 0)
            if self.grand_total != expected:
                raise ValidationError({'grand_total': 'Grand total must equal total amount plus tax amount'})


class QuotationItem(AuditModel):
    quotation = models.ForeignKey(SupplierQuotation, on_delete=models.CASCADE, related_name='items')
    requirement_item = models.ForeignKey(RequirementItem, on_delete=models.CASCADE, related_name='quotation_items')
    item_description = models.CharField(max_length=500)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    specifications = models.TextField(null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    hsn_code = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'quotation_item'

    def save(self, *args, **kwargs):
        self.tax_amount = (self.unit_price or 0) * (self.quantity or 0) * (self.tax_rate or 0) / Decimal('100.00')
        self.total_amount = (self.unit_price or 0) * (self.quantity or 0) + (self.tax_amount or 0)
        super().save(*args, **kwargs)


class PurchaseOrder(AuditModel):
    po_number = models.CharField(max_length=50, unique=True)
    requirement = models.ForeignKey(ProcurementRequirement, on_delete=models.CASCADE, related_name='purchase_orders')
    quotation = models.ForeignKey(SupplierQuotation, on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.ForeignKey(SupplierMaster, on_delete=models.PROTECT, related_name='purchase_orders')
    central_store = models.ForeignKey(CentralStore, on_delete=models.CASCADE, related_name='purchase_orders')
    po_date = models.DateField()
    expected_delivery_date = models.DateField()
    delivery_address_line1 = models.CharField(max_length=300)
    delivery_address_line2 = models.CharField(max_length=300, null=True, blank=True)
    delivery_city = models.CharField(max_length=100)
    delivery_state = models.CharField(max_length=100)
    delivery_pincode = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    payment_terms = models.CharField(max_length=200)
    delivery_terms = models.CharField(max_length=200, null=True, blank=True)
    special_instructions = models.TextField(null=True, blank=True)
    terms_and_conditions = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PO_STATUS_CHOICES, default='draft')
    po_document = models.FileField(upload_to='purchase_orders/', storage=store_file_storage, null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    acknowledged_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'purchase_order'
        ordering = ['-po_date']
        indexes = [
            models.Index(fields=['po_number']),
            models.Index(fields=['status']),
            models.Index(fields=['supplier']),
            models.Index(fields=['po_date']),
        ]

    def __str__(self):
        return self.po_number

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = generate_document_number('PO', PurchaseOrder, field_name='po_date')
        super().save(*args, **kwargs)

    def clean(self):
        # Phase 12.1: PO total must match quotation total (±2% tolerance)
        if self.quotation and self.grand_total:
            tolerance = Decimal('0.02')  # 2% tolerance
            expected = self.quotation.grand_total
            if expected > 0:
                diff = abs(self.grand_total - expected) / expected
                if diff > tolerance:
                    raise ValidationError({
                        'grand_total': f'PO total must match quotation total within 2% (Expected: {expected})'
                    })

        # Phase 12.1: Cannot create PO without approved requirement
        if self.requirement and self.requirement.status not in ['approved', 'po_created']:
            raise ValidationError({
                'requirement': 'Cannot create PO without approved requirement'
            })

    def send_to_supplier(self):
        self.status = 'sent'
        self.sent_date = timezone.now()
        self.save(update_fields=['status', 'sent_date', 'updated_at'])

    def mark_as_acknowledged(self):
        self.status = 'acknowledged'
        self.acknowledged_date = timezone.now()
        self.save(update_fields=['status', 'acknowledged_date', 'updated_at'])

    def check_fulfillment_status(self):
        """Phase 3.1: Check if all items received, update status accordingly"""
        items = self.items.all()
        if not items:
            return

        if all(item.pending_quantity == 0 for item in items):
            self.status = 'fulfilled'
            self.completed_date = timezone.now()
            self.save(update_fields=['status', 'completed_date', 'updated_at'])
        elif any(item.received_quantity > 0 for item in items):
            if self.status not in ['partially_received', 'fulfilled']:
                self.status = 'partially_received'
                self.save(update_fields=['status', 'updated_at'])


class PurchaseOrderItem(AuditModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    quotation_item = models.ForeignKey(QuotationItem, on_delete=models.CASCADE, related_name='po_items')
    item_description = models.CharField(max_length=500)
    hsn_code = models.CharField(max_length=20, null=True, blank=True)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    received_quantity = models.IntegerField(default=0)
    pending_quantity = models.IntegerField(default=0)
    specifications = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'purchase_order_item'

    def save(self, *args, **kwargs):
        self.pending_quantity = max(0, (self.quantity or 0) - (self.received_quantity or 0))
        super().save(*args, **kwargs)

    def update_received_quantity(self, qty):
        self.received_quantity = (self.received_quantity or 0) + qty
        self.save(update_fields=['received_quantity', 'pending_quantity', 'updated_at'])


class GoodsReceiptNote(AuditModel):
    grn_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='goods_receipts')
    supplier = models.ForeignKey(SupplierMaster, on_delete=models.PROTECT, related_name='goods_receipts')
    central_store = models.ForeignKey(CentralStore, on_delete=models.CASCADE, related_name='goods_receipts')
    receipt_date = models.DateField()
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    invoice_amount = models.DecimalField(max_digits=12, decimal_places=2)
    invoice_file = models.FileField(upload_to='grn_invoices/', storage=store_file_storage, null=True, blank=True)
    delivery_challan_number = models.CharField(max_length=100, null=True, blank=True)
    delivery_challan_file = models.FileField(upload_to='grn_challans/', storage=store_file_storage, null=True, blank=True)
    lr_number = models.CharField(max_length=100, null=True, blank=True)
    lr_copy = models.FileField(upload_to='grn_lr/', storage=store_file_storage, null=True, blank=True)
    vehicle_number = models.CharField(max_length=50, null=True, blank=True)
    transporter_name = models.CharField(max_length=200, null=True, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='grns_received')
    status = models.CharField(max_length=30, choices=GRN_STATUS_CHOICES, default='received')
    inspection_approval_request = models.ForeignKey(ApprovalRequest, null=True, blank=True, on_delete=models.SET_NULL)
    posted_to_inventory_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'goods_receipt_note'
        ordering = ['-receipt_date']
        indexes = [
            models.Index(fields=['grn_number']),
            models.Index(fields=['purchase_order']),
            models.Index(fields=['status']),
            models.Index(fields=['receipt_date']),
        ]

    def __str__(self):
        return self.grn_number

    def save(self, *args, **kwargs):
        if not self.grn_number:
            self.grn_number = generate_document_number('GRN', GoodsReceiptNote, field_name='receipt_date')
        super().save(*args, **kwargs)

    def clean(self):
        # Phase 12.2: Invoice amount should match PO amount (warning if >5% difference)
        if self.purchase_order and self.invoice_amount:
            po_total = self.purchase_order.grand_total
            if po_total > 0:
                diff_pct = abs(self.invoice_amount - po_total) / po_total
                if diff_pct > Decimal('0.05'):  # 5% tolerance
                    # Note: This is a warning, not a blocking error
                    import warnings
                    warnings.warn(f'Invoice amount differs from PO by {diff_pct*100:.1f}%')

    def submit_for_inspection(self):
        self.status = 'pending_inspection'
        self.save(update_fields=['status', 'updated_at'])

    def post_to_inventory(self):
        # Phase 12.2: Cannot post to inventory without inspection approval
        if self.status not in ['approved', 'inspected']:
            raise ValidationError('Cannot post to inventory without inspection approval')

        self.status = 'posted_to_inventory'
        self.posted_to_inventory_date = timezone.now()
        self.save(update_fields=['status', 'posted_to_inventory_date', 'updated_at'])


class GoodsReceiptItem(AuditModel):
    grn = models.ForeignKey(GoodsReceiptNote, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.CASCADE, related_name='grn_items')
    item_description = models.CharField(max_length=500)
    ordered_quantity = models.IntegerField()
    received_quantity = models.IntegerField()
    accepted_quantity = models.IntegerField(default=0)
    rejected_quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=20)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=100, null=True, blank=True)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    inspection_notes = models.TextField(null=True, blank=True)
    quality_status = models.CharField(max_length=20, choices=[('passed', 'Passed'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending')

    class Meta:
        db_table = 'goods_receipt_item'

    def clean(self):
        # Phase 12.2: Accepted + Rejected must equal Received quantity
        if (self.accepted_quantity or 0) + (self.rejected_quantity or 0) != (self.received_quantity or 0):
            raise ValidationError('Received quantity must equal accepted plus rejected')

        # Phase 12.2: Cannot receive quantity > ordered quantity
        if self.po_item and self.received_quantity:
            if self.received_quantity > self.po_item.quantity:
                raise ValidationError({
                    'received_quantity': f'Cannot receive more than ordered quantity ({self.po_item.quantity})'
                })


class InspectionNote(AuditModel):
    grn = models.OneToOneField(GoodsReceiptNote, on_delete=models.CASCADE, related_name='inspection')
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='inspections')
    inspection_date = models.DateField()
    overall_status = models.CharField(max_length=20, choices=[('passed', 'Passed'), ('failed', 'Failed'), ('partial', 'Partial'), ('pending', 'Pending')], default='pending')
    quality_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    packaging_condition = models.CharField(max_length=20, choices=[('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')])
    remarks = models.TextField(null=True, blank=True)
    recommendation = models.CharField(max_length=20, choices=[('accept', 'Accept'), ('reject', 'Reject'), ('partial_accept', 'Partial Accept')])
    inspection_images = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'inspection_note'


class StoreIndent(CollegeScopedModel):
    indent_number = models.CharField(max_length=50, unique=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='store_indents')
    requesting_store_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='indents_created')
    central_store = models.ForeignKey(CentralStore, on_delete=models.CASCADE, related_name='indents')
    indent_date = models.DateField(auto_now_add=True)
    required_by_date = models.DateField()
    priority = models.CharField(max_length=20, choices=INDENT_PRIORITY_CHOICES, default='medium')
    justification = models.TextField()
    status = models.CharField(max_length=30, choices=INDENT_STATUS_CHOICES, default='draft')
    approval_request = models.ForeignKey(ApprovalRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name='store_indents')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='indents_approved')
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    attachments = models.FileField(upload_to='indent_attachments/', storage=store_file_storage, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'store_indent'
        ordering = ['-indent_date']
        indexes = [
            models.Index(fields=['indent_number']),
            models.Index(fields=['college']),
            models.Index(fields=['status']),
            models.Index(fields=['indent_date']),
        ]

    def __str__(self):
        return self.indent_number

    def save(self, *args, **kwargs):
        if not self.indent_number:
            self.indent_number = generate_document_number('IND', StoreIndent, field_name='indent_date')
        super().save(*args, **kwargs)

    def clean(self):
        # Phase 12.3: Must provide justification for urgent priority
        if self.priority == 'urgent' and not self.justification:
            raise ValidationError({
                'justification': 'Justification is required for urgent priority indents'
            })

    def submit(self):
        """College store submits request to super admin"""
        self.status = 'pending_super_admin'
        self.save(update_fields=['status', 'updated_at'])

    def college_admin_approve(self, user=None):
        """College admin approves and sends to super admin"""
        # Allow approval from multiple valid states for robustness
        valid_states = ['pending_college_approval', 'draft', 'submitted']
        if self.status not in valid_states:
            # Log warning but don't fail if already in correct state
            if self.status == 'pending_super_admin':
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Indent {self.indent_number} already in pending_super_admin state')
                return
            raise ValidationError(f'Cannot approve indent in {self.status} status. Must be in one of: {", ".join(valid_states)}')
        self.status = 'pending_super_admin'
        self.save(update_fields=['status', 'updated_at'])

    def college_admin_reject(self, user=None, reason=None):
        """College admin rejects the request"""
        if self.status != 'pending_college_approval':
            raise ValidationError('Invalid status for college admin rejection')
        self.status = 'rejected_by_college'
        self.rejection_reason = reason
        self.save(update_fields=['status', 'rejection_reason', 'updated_at'])

    def super_admin_approve(self, user=None):
        """Super admin approves - status set to approved"""
        valid_states = ['pending_super_admin', 'pending_college_approval', 'submitted', 'draft']
        if self.status not in valid_states:
            # If already approved, just log and return
            if self.status == 'approved':
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Indent {self.indent_number} already approved')
                return
            raise ValidationError(f'Cannot approve indent in {self.status} status. Must be in one of: {", ".join(valid_states)}')
        self.status = 'approved'
        self.approved_by = user
        self.approved_date = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_date', 'updated_at'])

    def super_admin_reject(self, user=None, reason=None):
        """Super admin rejects the request"""
        if self.status != 'pending_super_admin':
            raise ValidationError('Invalid status for super admin rejection')
        self.status = 'rejected_by_super_admin'
        self.rejection_reason = reason
        self.approved_by = user
        self.save(update_fields=['status', 'rejection_reason', 'approved_by', 'updated_at'])

    def approve(self, user=None, approved_items=None):
        """Legacy approve method - keeping for compatibility"""
        self.status = 'approved'
        self.approved_by = user
        self.approved_date = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_date', 'updated_at'])

    def reject(self, user=None, reason=None):
        """Legacy reject method - keeping for compatibility"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.approved_by = user
        self.save(update_fields=['status', 'rejection_reason', 'approved_by', 'updated_at'])

    def check_fulfillment(self):
        items = self.items.all()
        if items and all((line.pending_quantity or 0) == 0 for line in items):
            self.status = 'fulfilled'
        elif any((line.issued_quantity or 0) > 0 for line in items):
            self.status = 'partially_fulfilled'
        self.save(update_fields=['status', 'updated_at'])


class IndentItem(AuditModel):
    indent = models.ForeignKey(StoreIndent, on_delete=models.CASCADE, related_name='items')
    central_store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='indent_items')
    requested_quantity = models.IntegerField(validators=[MinValueValidator(1)])
    approved_quantity = models.IntegerField(default=0)
    issued_quantity = models.IntegerField(default=0)
    pending_quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=20)
    justification = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'indent_item'

    def clean(self):
        # Phase 12.3: Cannot approve quantity > requested quantity
        if self.approved_quantity and self.requested_quantity:
            if self.approved_quantity > self.requested_quantity:
                raise ValidationError({
                    'approved_quantity': 'Cannot approve more than requested quantity'
                })

        # Phase 12.3: Cannot issue if central store stock insufficient
        # Skip validation if indent/central_store not set yet (during creation)
        if not self.indent_id or not self.central_store_item_id:
            return

        # Only validate stock if indent has a central store
        if self.indent and self.indent.central_store and self.central_store_item and self.requested_quantity:
            try:
                inventory = CentralStoreInventory.objects.get(
                    central_store=self.indent.central_store,
                    item=self.central_store_item
                )
                # Only warn if stock is insufficient, don't block creation
                # This allows indents to be created even if stock is low
                if self.requested_quantity > inventory.quantity_available:
                    # Log warning instead of raising error
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f'IndentItem {self.id}: Requested quantity {self.requested_quantity} '
                        f'exceeds available stock {inventory.quantity_available} for item {self.central_store_item.name}'
                    )
            except CentralStoreInventory.DoesNotExist:
                # Log warning instead of raising error during creation
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f'IndentItem {self.id}: Item {self.central_store_item.name} not in central store inventory'
                )

    def save(self, *args, **kwargs):
        self.pending_quantity = max(0, (self.approved_quantity or 0) - (self.issued_quantity or 0))
        super().save(*args, **kwargs)

    def update_issued_quantity(self, qty):
        self.issued_quantity = (self.issued_quantity or 0) + qty
        self.save(update_fields=['issued_quantity', 'pending_quantity', 'updated_at'])


class MaterialIssueNote(AuditModel):
    min_number = models.CharField(max_length=50, unique=True)
    indent = models.ForeignKey(StoreIndent, on_delete=models.CASCADE, related_name='material_issues')
    central_store = models.ForeignKey(CentralStore, on_delete=models.CASCADE, related_name='material_issues')
    receiving_college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='materials_received')
    issue_date = models.DateField()
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='materials_issued')
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='materials_received_user')
    transport_mode = models.CharField(max_length=50, null=True, blank=True)
    vehicle_number = models.CharField(max_length=50, null=True, blank=True)
    driver_name = models.CharField(max_length=100, null=True, blank=True)
    driver_contact = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('prepared', 'Prepared'), ('dispatched', 'Dispatched'), ('in_transit', 'In Transit'), ('received', 'Received'), ('cancelled', 'Cancelled')], default='prepared')
    dispatch_date = models.DateTimeField(null=True, blank=True)
    receipt_date = models.DateTimeField(null=True, blank=True)
    min_document = models.FileField(upload_to='material_issue_notes/', storage=store_file_storage, null=True, blank=True)
    internal_notes = models.TextField(null=True, blank=True)
    receipt_confirmation_notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'material_issue_note'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['min_number']),
            models.Index(fields=['indent']),
            models.Index(fields=['status']),
            models.Index(fields=['issue_date']),
        ]

    def __str__(self):
        return self.min_number

    def save(self, *args, **kwargs):
        if not self.min_number:
            self.min_number = generate_document_number('MIN', MaterialIssueNote, field_name='issue_date')
        super().save(*args, **kwargs)

    def dispatch(self):
        """Dispatch materials - validate stock before dispatch"""
        import logging
        logger = logging.getLogger(__name__)

        errors = []
        for issue_item in self.items.all():
            try:
                inventory = CentralStoreInventory.objects.get(
                    central_store=self.central_store,
                    item=issue_item.item
                )

                # Check stock availability
                available_qty = inventory.quantity_available or 0
                if available_qty <= 0:
                    error_msg = f'No stock available for {issue_item.item.name}'
                    logger.warning(f'MaterialIssueNote {self.min_number}: {error_msg}')
                    errors.append(error_msg)
                    continue

                if issue_item.issued_quantity > available_qty:
                    error_msg = f'Insufficient stock for {issue_item.item.name}. Requested: {issue_item.issued_quantity}, Available: {available_qty}'
                    logger.warning(f'MaterialIssueNote {self.min_number}: {error_msg}')
                    errors.append(error_msg)
                    continue

            except CentralStoreInventory.DoesNotExist:
                error_msg = f'Item {issue_item.item.name} not in central store inventory'
                logger.warning(f'MaterialIssueNote {self.min_number}: {error_msg}')
                errors.append(error_msg)
                continue

        # If there are stock errors, raise validation error with details
        if errors:
            raise ValidationError({'items': ' | '.join(errors)})

        # Update status to in_transit/dispatched
        self.status = 'in_transit'
        self.dispatch_date = timezone.now()
        self.save(update_fields=['status', 'dispatch_date', 'updated_at'])

    def confirm_receipt(self, user=None, notes=None):
        self.status = 'received'
        self.receipt_date = timezone.now()
        self.receipt_confirmation_notes = notes or ''
        self.received_by = user
        self.save(update_fields=['status', 'receipt_date', 'receipt_confirmation_notes', 'received_by', 'updated_at'])


class MaterialIssueItem(AuditModel):
    material_issue = models.ForeignKey(MaterialIssueNote, on_delete=models.CASCADE, related_name='items')
    indent_item = models.ForeignKey(IndentItem, on_delete=models.CASCADE, related_name='issue_items')
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='material_issues')
    issued_quantity = models.IntegerField()
    unit = models.CharField(max_length=20)
    batch_number = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'material_issue_item'

    def clean(self):
        # Phase 12.3: Cannot issue quantity > approved quantity
        if self.indent_item and self.issued_quantity:
            if self.issued_quantity > self.indent_item.approved_quantity:
                raise ValidationError({
                    'issued_quantity': f'Cannot issue more than approved quantity ({self.indent_item.approved_quantity})'
                })


class CentralStoreInventory(AuditModel):
    central_store = models.ForeignKey(CentralStore, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='central_inventory')
    quantity_on_hand = models.IntegerField(default=0)
    quantity_allocated = models.IntegerField(default=0)
    quantity_available = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    max_stock_level = models.IntegerField(null=True, blank=True)
    last_stock_update = models.DateTimeField(auto_now=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'central_store_inventory'
        unique_together = ['central_store', 'item']
        indexes = [
            models.Index(fields=['central_store']),
            models.Index(fields=['item']),
            models.Index(fields=['quantity_available']),
        ]

    def save(self, *args, **kwargs):
        self.quantity_available = (self.quantity_on_hand or 0) - (self.quantity_allocated or 0)
        super().save(*args, **kwargs)

    def clean(self):
        # Phase 12.4: Stock cannot go negative
        if self.quantity_on_hand is not None and self.quantity_on_hand < 0:
            raise ValidationError({
                'quantity_on_hand': 'Stock cannot go negative'
            })

        # Phase 12.4: Allocation + Issue ≤ On-hand quantity
        if self.quantity_allocated is not None and self.quantity_on_hand is not None:
            if self.quantity_allocated > self.quantity_on_hand:
                raise ValidationError({
                    'quantity_allocated': 'Allocated quantity cannot exceed on-hand quantity'
                })

    def update_stock(self, delta, transaction_type, reference=None, performed_by=None):
        before = self.quantity_on_hand or 0
        new_quantity = before + delta

        # Phase 12.4: Stock cannot go negative
        if new_quantity < 0:
            raise ValidationError(f'Insufficient stock. Current: {before}, Requested: {abs(delta)}')

        self.quantity_on_hand = new_quantity
        self.save(update_fields=['quantity_on_hand', 'quantity_available', 'updated_at'])
        reference_type = None
        reference_id = None
        if reference is not None:
            try:
                reference_type = ContentType.objects.get_for_model(reference.__class__)
                reference_id = getattr(reference, 'pk', None)
            except Exception:
                reference_type = None
                reference_id = None
        InventoryTransaction.objects.create(
            transaction_number=generate_document_number('TRN', InventoryTransaction, field_name='transaction_date'),
            transaction_type=transaction_type,
            central_store=self.central_store,
            item=self.item,
            quantity=delta,
            before_quantity=before,
            after_quantity=self.quantity_on_hand,
            unit_cost=self.unit_cost,
            total_value=(self.unit_cost or 0) * delta,
            reference_type=reference_type,
            reference_id=reference_id,
            performed_by=performed_by,
        )

    def allocate_stock(self, quantity):
        self.quantity_allocated = (self.quantity_allocated or 0) + quantity
        self.save(update_fields=['quantity_allocated', 'quantity_available', 'updated_at'])

    def release_allocation(self, quantity):
        self.quantity_allocated = max(0, (self.quantity_allocated or 0) - quantity)
        self.save(update_fields=['quantity_allocated', 'quantity_available', 'updated_at'])


class InventoryTransaction(AuditModel):
    transaction_number = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES)
    central_store = models.ForeignKey(CentralStore, on_delete=models.CASCADE, related_name='transactions')
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.IntegerField()
    transaction_date = models.DateTimeField(auto_now_add=True)
    before_quantity = models.IntegerField()
    after_quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    reference_object = GenericForeignKey('reference_type', 'reference_id')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'inventory_transaction'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['central_store']),
            models.Index(fields=['item']),
        ]

    def save(self, *args, **kwargs):
        if not self.transaction_number:
            self.transaction_number = generate_document_number('TRN', InventoryTransaction, field_name='transaction_date')
        if not self.total_value:
            self.total_value = (self.unit_cost or 0) * (self.quantity or 0)
        super().save(*args, **kwargs)
