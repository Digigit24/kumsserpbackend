"""
DRF Serializers for Library app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    BookCategory,
    Book,
    LibraryMember,
    LibraryCard,
    BookIssue,
    BookReturn,
    LibraryFine,
    BookReservation,
)
from apps.core.serializers import UserBasicSerializer, TenantAuditMixin

User = get_user_model()


# ============================================================================
# BOOK CATEGORY SERIALIZERS
# ============================================================================


class BookCategorySerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for BookCategory model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = BookCategory
        fields = [
            'id', 'college', 'college_name', 'name', 'code', 'description', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# BOOK SERIALIZERS
# ============================================================================


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for listing books (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'college', 'college_name', 'category', 'category_name',
            'title', 'author', 'isbn', 'publisher', 'quantity',
            'available_quantity', 'location', 'is_active'
        ]
        read_only_fields = ['id', 'college_name', 'category_name']


class BookSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Book model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'college', 'college_name', 'category', 'category_name',
            'title', 'author', 'isbn', 'publisher', 'edition',
            'publication_year', 'language', 'pages', 'quantity',
            'available_quantity', 'price', 'location', 'barcode',
            'description', 'cover_image', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'category_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# LIBRARY MEMBER SERIALIZERS
# ============================================================================


class LibraryMemberListSerializer(serializers.ModelSerializer):
    """Serializer for listing library members (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    member_type_display = serializers.CharField(source='get_member_type_display', read_only=True)

    class Meta:
        model = LibraryMember
        fields = [
            'id', 'college', 'college_name', 'member_type', 'member_type_display',
            'student', 'student_name', 'teacher', 'teacher_name',
            'member_id', 'joining_date', 'max_books_allowed', 'is_active'
        ]
        read_only_fields = ['id', 'college_name', 'student_name', 'teacher_name', 'member_type_display']


class LibraryMemberSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for LibraryMember model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    member_type_display = serializers.CharField(source='get_member_type_display', read_only=True)

    class Meta:
        model = LibraryMember
        fields = [
            'id', 'college', 'college_name', 'member_type', 'member_type_display',
            'student', 'student_name', 'teacher', 'teacher_name',
            'member_id', 'joining_date', 'max_books_allowed', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'student_name', 'teacher_name', 'member_type_display',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# LIBRARY CARD SERIALIZERS
# ============================================================================


class LibraryCardSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for LibraryCard model."""
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    student_name = serializers.CharField(source='member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='member.teacher.get_full_name', read_only=True)

    class Meta:
        model = LibraryCard
        fields = [
            'id', 'member', 'member_id', 'student_name', 'teacher_name',
            'card_number', 'issue_date', 'valid_until', 'card_file',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'member_id', 'student_name', 'teacher_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# BOOK ISSUE SERIALIZERS
# ============================================================================


class BookIssueListSerializer(serializers.ModelSerializer):
    """Serializer for listing book issues (minimal fields)."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    student_name = serializers.CharField(source='member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='member.teacher.get_full_name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BookIssue
        fields = [
            'id', 'book', 'book_title', 'member', 'member_id',
            'student_name', 'teacher_name',
            'issue_date', 'due_date', 'return_date',
            'status', 'status_display', 'issued_by', 'issued_by_name'
        ]
        read_only_fields = [
            'id', 'book_title', 'member_id', 'student_name', 'teacher_name',
            'status_display', 'issued_by_name'
        ]


class BookIssueSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for BookIssue model."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    student_name = serializers.CharField(source='member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='member.teacher.get_full_name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BookIssue
        fields = [
            'id', 'book', 'book_title', 'member', 'member_id',
            'student_name', 'teacher_name',
            'issue_date', 'due_date', 'return_date',
            'status', 'status_display', 'remarks',
            'issued_by', 'issued_by_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'book_title', 'member_id', 'student_name', 'teacher_name',
            'status_display', 'issued_by_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# BOOK RETURN SERIALIZERS
# ============================================================================


class BookReturnSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for BookReturn model."""
    book_title = serializers.CharField(source='issue.book.title', read_only=True)
    member_id = serializers.CharField(source='issue.member.member_id', read_only=True)
    student_name = serializers.CharField(source='issue.member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='issue.member.teacher.get_full_name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)

    class Meta:
        model = BookReturn
        fields = [
            'id', 'issue', 'book_title', 'member_id', 'student_name', 'teacher_name',
            'return_date', 'fine_amount', 'is_damaged', 'damage_charges',
            'remarks', 'received_by', 'received_by_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'book_title', 'member_id', 'student_name', 'teacher_name',
            'received_by_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# LIBRARY FINE SERIALIZERS
# ============================================================================


class LibraryFineListSerializer(serializers.ModelSerializer):
    """Serializer for listing library fines (minimal fields)."""
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    student_name = serializers.CharField(source='member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='member.teacher.get_full_name', read_only=True)
    book_title = serializers.CharField(source='book_issue.book.title', read_only=True)

    class Meta:
        model = LibraryFine
        fields = [
            'id', 'member', 'member_id', 'student_name', 'teacher_name',
            'book_issue', 'book_title', 'amount', 'fine_date',
            'is_paid', 'paid_date'
        ]
        read_only_fields = ['id', 'member_id', 'student_name', 'teacher_name', 'book_title']


class LibraryFineSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for LibraryFine model."""
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    student_name = serializers.CharField(source='member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='member.teacher.get_full_name', read_only=True)
    book_title = serializers.CharField(source='book_issue.book.title', read_only=True)

    class Meta:
        model = LibraryFine
        fields = [
            'id', 'member', 'member_id', 'student_name', 'teacher_name',
            'book_issue', 'book_title', 'amount', 'reason', 'fine_date',
            'is_paid', 'paid_date', 'remarks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'member_id', 'student_name', 'teacher_name', 'book_title',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# BOOK RESERVATION SERIALIZERS
# ============================================================================


class BookReservationListSerializer(serializers.ModelSerializer):
    """Serializer for listing book reservations (minimal fields)."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    student_name = serializers.CharField(source='member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='member.teacher.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BookReservation
        fields = [
            'id', 'book', 'book_title', 'member', 'member_id',
            'student_name', 'teacher_name', 'reservation_date',
            'status', 'status_display'
        ]
        read_only_fields = [
            'id', 'book_title', 'member_id', 'student_name',
            'teacher_name', 'status_display'
        ]


class BookReservationSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for BookReservation model."""
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_id = serializers.CharField(source='member.member_id', read_only=True)
    student_name = serializers.CharField(source='member.student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='member.teacher.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = BookReservation
        fields = [
            'id', 'book', 'book_title', 'member', 'member_id',
            'student_name', 'teacher_name', 'reservation_date',
            'status', 'status_display', 'remarks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'book_title', 'member_id', 'student_name',
            'teacher_name', 'status_display',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================


class BulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk delete operations."""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of IDs to delete"
    )
