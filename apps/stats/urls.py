from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardStatsViewSet,
    AcademicStatsViewSet,
    FinancialStatsViewSet,
    LibraryStatsViewSet,
    HRStatsViewSet,
    StoreStatsViewSet,
    HostelStatsViewSet,
    CommunicationStatsViewSet,
    MyStatsViewSet,
    MyTeacherStatsViewSet,
)

app_name = 'stats'

router = DefaultRouter()

# Personal Statistics (Role-based)
router.register(r'my', MyStatsViewSet, basename='my-stats')  # For students
router.register(r'my-teacher', MyTeacherStatsViewSet, basename='my-teacher-stats')  # For teachers

# College-wide Statistics (Admin/Staff)
router.register(r'dashboard', DashboardStatsViewSet, basename='dashboard-stats')
router.register(r'academic', AcademicStatsViewSet, basename='academic-stats')
router.register(r'financial', FinancialStatsViewSet, basename='financial-stats')
router.register(r'library', LibraryStatsViewSet, basename='library-stats')
router.register(r'hr', HRStatsViewSet, basename='hr-stats')
router.register(r'store', StoreStatsViewSet, basename='store-stats')
router.register(r'hostel', HostelStatsViewSet, basename='hostel-stats')
router.register(r'communication', CommunicationStatsViewSet, basename='communication-stats')

urlpatterns = [
    path('', include(router.urls)),
]
