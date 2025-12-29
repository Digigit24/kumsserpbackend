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
)

app_name = 'stats'

router = DefaultRouter()

# Register all statistics ViewSets
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
