"""
Library models for book catalog, circulation, and fines.
"""
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.models import CollegeScopedModel, AuditModel, College
from apps.students.models import Student
from apps.teachers.models import Teacher


class MemberType(models.TextChoices):
    STUDENT = 'student', 'Student'
    TEACHER = 'teacher', 'Teacher'


class IssueStatus(models.TextChoices):
    ISSUED = 'issued', 'Issued'
    RETURNED = 'returned', 'Returned'
    OVERDUE = 'overdue', 'Overdue'


class ReservationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    CANCELLED = 'cancelled', 'Cancelled'
    FULFILLED = 'fulfilled', 'Fulfilled'


class BookCategory(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='book_categories',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Category name")
    code = models.CharField(max_length=20, help_text="Category code")
    description = models.TextField(null=True, blank=True, help_text="Description")

    class Meta:
        db_table = 'book_category'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
            models.Index(fields=['college', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Book(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='books',
        help_text="College reference"
    )
    category = models.ForeignKey(
        BookCategory,
        on_delete=models.CASCADE,
        related_name='books',
        help_text="Category"
    )
    title = models.CharField(max_length=300, help_text="Book title")
    author = models.CharField(max_length=200, help_text="Author")
    isbn = models.CharField(max_length=20, null=True, blank=True, help_text="ISBN")
    publisher = models.CharField(max_length=200, null=True, blank=True, help_text="Publisher")
    edition = models.CharField(max_length=50, null=True, blank=True, help_text="Edition")
    publication_year = models.IntegerField(null=True, blank=True, help_text="Publication year")
    language = models.CharField(max_length=50, null=True, blank=True, help_text="Language")
    pages = models.IntegerField(null=True, blank=True, help_text="Number of pages")
    quantity = models.IntegerField(help_text="Total quantity")
    available_quantity = models.IntegerField(help_text="Available quantity")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price")
    location = models.CharField(max_length=100, null=True, blank=True, help_text="Shelf location")
    barcode = models.CharField(max_length=50, null=True, blank=True, help_text="Barcode")
    description = models.TextField(null=True, blank=True, help_text="Description")
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True, help_text="Cover image")

    class Meta:
        db_table = 'book'
        indexes = [
            models.Index(fields=['college', 'category']),
            models.Index(fields=['isbn']),
            models.Index(fields=['barcode']),
            models.Index(fields=['title']),
            models.Index(fields=['college', 'is_active']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.available_quantity is not None and self.quantity is not None:
            if self.available_quantity < 0:
                raise ValidationError("Available quantity cannot be negative.")
            if self.available_quantity > self.quantity:
                raise ValidationError("Available quantity cannot exceed total quantity.")

    def save(self, *args, **kwargs):
        if self.available_quantity is None:
            self.available_quantity = self.quantity
        if self.quantity is not None and self.available_quantity is not None:
            self.available_quantity = max(0, min(self.available_quantity, self.quantity))
        super().save(*args, **kwargs)


class LibraryMember(CollegeScopedModel):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='library_members',
        help_text="College reference"
    )
    member_type = models.CharField(
        max_length=20,
        choices=MemberType.choices,
        help_text="Type (student/teacher)"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='library_memberships',
        help_text="Student"
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='library_memberships',
        help_text="Teacher"
    )
    member_id = models.CharField(max_length=50, unique=True, help_text="Member ID")
    joining_date = models.DateField(help_text="Joining date")
    max_books_allowed = models.IntegerField(default=3, help_text="Max books")

    class Meta:
        db_table = 'library_member'
        indexes = [
            models.Index(fields=['college', 'member_id']),
            models.Index(fields=['student']),
            models.Index(fields=['teacher']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'student'],
                name='unique_library_member_student',
                condition=Q(student__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['college', 'teacher'],
                name='unique_library_member_teacher',
                condition=Q(teacher__isnull=False)
            ),
        ]

    def __str__(self):
        return f"{self.member_id} ({self.get_member_type_display()})"

    def clean(self):
        if self.member_type == MemberType.STUDENT and not self.student:
            raise ValidationError("Student member type requires a student reference.")
        if self.member_type == MemberType.TEACHER and not self.teacher:
            raise ValidationError("Teacher member type requires a teacher reference.")
        if self.student and self.teacher:
            raise ValidationError("A library member cannot be linked to both student and teacher.")


class LibraryCard(AuditModel):
    member = models.ForeignKey(
        LibraryMember,
        on_delete=models.CASCADE,
        related_name='cards',
        help_text="Member"
    )
    card_number = models.CharField(max_length=50, unique=True, help_text="Card number")
    issue_date = models.DateField(help_text="Issue date")
    valid_until = models.DateField(help_text="Valid until")
    card_file = models.FileField(upload_to='library_cards/', null=True, blank=True, help_text="Card PDF")

    class Meta:
        db_table = 'library_card'
        indexes = [
            models.Index(fields=['member', 'card_number']),
        ]

    def __str__(self):
        return f"Card {self.card_number}"


class BookIssue(AuditModel):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='issues',
        help_text="Book"
    )
    member = models.ForeignKey(
        LibraryMember,
        on_delete=models.CASCADE,
        related_name='issues',
        help_text="Member"
    )
    issue_date = models.DateField(help_text="Issue date")
    due_date = models.DateField(help_text="Due date")
    return_date = models.DateField(null=True, blank=True, help_text="Return date")
    status = models.CharField(
        max_length=20,
        choices=IssueStatus.choices,
        default=IssueStatus.ISSUED,
        help_text="Status"
    )
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='library_issues',
        help_text="Issued by"
    )

    class Meta:
        db_table = 'book_issue'
        indexes = [
            models.Index(fields=['book', 'member']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.book} -> {self.member}"

    def clean(self):
        if self.due_date and self.issue_date and self.due_date < self.issue_date:
            raise ValidationError("Due date cannot be before issue date.")
        if self.book and self.member and self.book.college_id != self.member.college_id:
            raise ValidationError("Book and member must belong to the same college.")


class BookReturn(AuditModel):
    issue = models.ForeignKey(
        BookIssue,
        on_delete=models.CASCADE,
        related_name='returns',
        help_text="Issue"
    )
    return_date = models.DateField(help_text="Return date")
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), help_text="Fine amount")
    is_damaged = models.BooleanField(default=False, help_text="Damaged flag")
    damage_charges = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), help_text="Damage charges")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='library_returns_received',
        help_text="Received by"
    )

    class Meta:
        db_table = 'book_return'
        indexes = [
            models.Index(fields=['issue', 'return_date']),
        ]

    def __str__(self):
        return f"Return for {self.issue}"

    def clean(self):
        if self.issue and self.issue.due_date and self.return_date and self.return_date < self.issue.issue_date:
            raise ValidationError("Return date cannot be before issue date.")


class LibraryFine(AuditModel):
    member = models.ForeignKey(
        LibraryMember,
        on_delete=models.CASCADE,
        related_name='library_fines',
        help_text="Member"
    )
    book_issue = models.ForeignKey(
        BookIssue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='library_fines',
        help_text="Book issue"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2, help_text="Amount")
    reason = models.TextField(help_text="Reason")
    fine_date = models.DateField(help_text="Fine date")
    is_paid = models.BooleanField(default=False, help_text="Paid status")
    paid_date = models.DateField(null=True, blank=True, help_text="Paid date")
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")

    class Meta:
        db_table = 'library_fine'
        indexes = [
            models.Index(fields=['member', 'fine_date', 'is_paid']),
        ]

    def __str__(self):
        return f"Fine {self.amount} for {self.member}"


class BookReservation(AuditModel):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="Book"
    )
    member = models.ForeignKey(
        LibraryMember,
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text="Member"
    )
    reservation_date = models.DateField(help_text="Reservation date")
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
        help_text="Status"
    )
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")

    class Meta:
        db_table = 'book_reservation'
        indexes = [
            models.Index(fields=['book', 'member', 'reservation_date', 'status']),
        ]

    def __str__(self):
        return f"Reservation for {self.book} by {self.member}"

    def clean(self):
        if self.book and self.member and self.book.college_id != self.member.college_id:
            raise ValidationError("Book and member must belong to the same college.")
