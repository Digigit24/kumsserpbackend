from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal

from apps.library.models import Book, BookIssue, LibraryFine, LibraryMember


class LibraryStatsService:
    """Service class for library statistics calculations"""

    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_circulation_stats(self):
        """Calculate library circulation statistics"""
        # Book stats
        books = Book.objects.filter(college_id=self.college_id, is_active=True)
        total_books = books.aggregate(total=Coalesce(Sum('quantity'), 0))['total']
        available_books = books.aggregate(total=Coalesce(Sum('available_quantity'), 0))['total']
        issued_books = total_books - available_books

        # Issue stats
        issues = BookIssue.objects.filter(book__college_id=self.college_id)

        if self.filters.get('from_date'):
            issues = issues.filter(issue_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            issues = issues.filter(issue_date__lte=self.filters['to_date'])

        total_issues = issues.count()
        total_returns = issues.filter(status='RETURNED').count()
        overdue_books = issues.filter(
            status='ISSUED',
            due_date__lt=timezone.now().date()
        ).count()

        # Fine stats
        fines = LibraryFine.objects.filter(member__college_id=self.college_id)

        if self.filters.get('from_date'):
            fines = fines.filter(fine_date__gte=self.filters['from_date'])
        if self.filters.get('to_date'):
            fines = fines.filter(fine_date__lte=self.filters['to_date'])

        total_fines_collected = fines.filter(is_paid=True).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        outstanding_fines = fines.filter(is_paid=False).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0'))
        )['total']

        # Popular books
        popular_books_qs = issues.values(
            'book__id',
            'book__title',
            'book__author',
            'book__isbn',
            'book__category__name'
        ).annotate(
            issue_count=Count('id')
        ).order_by('-issue_count')[:10]

        popular_books = []
        for book in popular_books_qs:
            popular_books.append({
                'book_id': book['book__id'],
                'title': book['book__title'],
                'author': book['book__author'],
                'isbn': book['book__isbn'],
                'issue_count': book['issue_count'],
                'category': book['book__category__name'] or 'Uncategorized'
            })

        # Active members
        active_members = LibraryMember.objects.filter(
            college_id=self.college_id,
            is_active=True
        ).count()

        return {
            'total_books': total_books,
            'available_books': available_books,
            'issued_books': issued_books,
            'total_issues': total_issues,
            'total_returns': total_returns,
            'overdue_books': overdue_books,
            'total_fines_collected': total_fines_collected,
            'outstanding_fines': outstanding_fines,
            'popular_books': popular_books,
            'active_members': active_members,
        }
