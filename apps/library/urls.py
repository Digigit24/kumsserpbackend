"""
URL configuration for Library app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookCategoryViewSet,
    BookViewSet,
    LibraryMemberViewSet,
    LibraryCardViewSet,
    BookIssueViewSet,
    BookReturnViewSet,
    LibraryFineViewSet,
    BookReservationViewSet,
)

router = DefaultRouter()
router.register(r'categories', BookCategoryViewSet, basename='bookcategory')
router.register(r'books', BookViewSet, basename='book')
router.register(r'members', LibraryMemberViewSet, basename='librarymember')
router.register(r'cards', LibraryCardViewSet, basename='librarycard')
router.register(r'issues', BookIssueViewSet, basename='bookissue')
router.register(r'returns', BookReturnViewSet, basename='bookreturn')
router.register(r'fines', LibraryFineViewSet, basename='libraryfine')
router.register(r'reservations', BookReservationViewSet, basename='bookreservation')

urlpatterns = [
    path('', include(router.urls)),
]
