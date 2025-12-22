from django.contrib import admin

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


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('college', 'is_active')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'college', 'available_quantity', 'is_active')
    search_fields = ('title', 'author', 'isbn', 'barcode')
    list_filter = ('college', 'category', 'language', 'is_active')


@admin.register(LibraryMember)
class LibraryMemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'member_type', 'college', 'student', 'teacher', 'joining_date', 'is_active')
    search_fields = ('member_id',)
    list_filter = ('member_type', 'college', 'is_active')


@admin.register(LibraryCard)
class LibraryCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'member', 'issue_date', 'valid_until', 'is_active')
    search_fields = ('card_number',)
    list_filter = ('is_active',)


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'issue_date', 'due_date', 'status', 'is_active')
    search_fields = ('book__title', 'member__member_id')
    list_filter = ('status', 'issue_date', 'due_date', 'is_active')


@admin.register(BookReturn)
class BookReturnAdmin(admin.ModelAdmin):
    list_display = ('issue', 'return_date', 'fine_amount', 'damage_charges', 'is_active')
    list_filter = ('return_date', 'is_active')


@admin.register(LibraryFine)
class LibraryFineAdmin(admin.ModelAdmin):
    list_display = ('member', 'book_issue', 'amount', 'fine_date', 'is_paid', 'is_active')
    search_fields = ('member__member_id',)
    list_filter = ('is_paid', 'fine_date', 'is_active')


@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'reservation_date', 'status', 'is_active')
    list_filter = ('status', 'reservation_date', 'is_active')
