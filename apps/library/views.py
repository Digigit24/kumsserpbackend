from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedMixin, CollegeScopedModelViewSet
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
from .serializers import (
    BookCategorySerializer,
    BookSerializer,
    LibraryMemberSerializer,
    LibraryCardSerializer,
    BookIssueSerializer,
    BookReturnSerializer,
    LibraryFineSerializer,
    BookReservationSerializer,
)


class LibraryScopedModelViewSet(CollegeScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet that scopes by college using a related lookup path instead of a direct FK.
    """
    related_college_lookup = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        college_id = self.get_college_id(required=False)
        user = getattr(self.request, 'user', None)

        if college_id == 'all' or (user and (user.is_superuser or user.is_staff) and not college_id):
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        if not self.related_college_lookup:
            return queryset.none()

        return queryset.filter(**{self.related_college_lookup: college_id})


class BookCategoryViewSet(CollegeScopedModelViewSet):
    queryset = BookCategory.objects.all()
    serializer_class = BookCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class BookViewSet(CollegeScopedModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'language', 'is_active']
    search_fields = ['title', 'author', 'isbn', 'barcode']
    ordering_fields = ['title', 'author', 'publication_year', 'available_quantity', 'created_at']
    ordering = ['title']


class LibraryMemberViewSet(CollegeScopedModelViewSet):
    queryset = LibraryMember.objects.all()
    serializer_class = LibraryMemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['member_type', 'student', 'teacher', 'is_active']
    search_fields = ['member_id']
    ordering_fields = ['joining_date', 'member_id', 'created_at']
    ordering = ['-joining_date']


class LibraryCardViewSet(LibraryScopedModelViewSet):
    queryset = LibraryCard.objects.select_related('member')
    serializer_class = LibraryCardSerializer
    related_college_lookup = 'member__college_id'
    filterset_fields = ['member', 'is_active']
    search_fields = ['card_number']
    ordering_fields = ['issue_date', 'valid_until', 'card_number', 'created_at']
    ordering = ['-issue_date']


class BookIssueViewSet(LibraryScopedModelViewSet):
    queryset = BookIssue.objects.select_related('book', 'member')
    serializer_class = BookIssueSerializer
    related_college_lookup = 'book__college_id'
    filterset_fields = ['book', 'member', 'status', 'issue_date', 'due_date', 'is_active']
    search_fields = ['book__title', 'member__member_id']
    ordering_fields = ['issue_date', 'due_date', 'created_at']
    ordering = ['-issue_date']


class BookReturnViewSet(LibraryScopedModelViewSet):
    queryset = BookReturn.objects.select_related('issue', 'issue__book', 'issue__member')
    serializer_class = BookReturnSerializer
    related_college_lookup = 'issue__book__college_id'
    filterset_fields = ['issue', 'return_date', 'is_active']
    ordering_fields = ['return_date', 'created_at']
    ordering = ['-return_date']


class LibraryFineViewSet(LibraryScopedModelViewSet):
    queryset = LibraryFine.objects.select_related('member', 'book_issue')
    serializer_class = LibraryFineSerializer
    related_college_lookup = 'member__college_id'
    filterset_fields = ['member', 'book_issue', 'fine_date', 'is_paid', 'is_active']
    ordering_fields = ['fine_date', 'amount', 'created_at']
    ordering = ['-fine_date']


class BookReservationViewSet(LibraryScopedModelViewSet):
    queryset = BookReservation.objects.select_related('book', 'member')
    serializer_class = BookReservationSerializer
    related_college_lookup = 'book__college_id'
    filterset_fields = ['book', 'member', 'status', 'reservation_date', 'is_active']
    ordering_fields = ['reservation_date', 'created_at']
    ordering = ['-reservation_date']
