from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from datetime import datetime

from apps.core.mixins import CollegeScopedMixin
from apps.core.models import College
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.accounts.models import User
from apps.academic.models import Class
from .serializers import (
    AcademicStatsSerializer,
    FinancialStatsSerializer,
    LibraryCirculationStatsSerializer,
    HRStatsSerializer,
    StoreSalesStatsSerializer,
    InventoryStatsSerializer,
    HostelOccupancyStatsSerializer,
    HostelFeeStatsSerializer,
    CommunicationStatsSerializer,
    DashboardStatsSerializer,
    AcademicPerformanceStatsSerializer,
    AttendanceStatsSerializer,
    AssignmentStatsSerializer,
    FeeCollectionStatsSerializer,
    ExpenseStatsSerializer,
    IncomeStatsSerializer,
)
from .services.academic_stats import AcademicStatsService
from .services.financial_stats import FinancialStatsService
from .services.library_stats import LibraryStatsService
from .services.hr_stats import HRStatsService
from .services.store_stats import StoreStatsService
from .services.hostel_stats import HostelStatsService
from .services.communication_stats import CommunicationStatsService
from .services.dashboard_stats import DashboardStatsService


class StatsFilterMixin:
    """Mixin to parse common statistics filters from query parameters"""

    def parse_filters(self, request):
        """Parse query parameters into filter dictionary"""
        filters = {}

        # Date range
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if from_date:
            try:
                filters['from_date'] = datetime.strptime(from_date, '%Y-%m-%d').date()
            except ValueError:
                pass

        if to_date:
            try:
                filters['to_date'] = datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Academic year
        academic_year = request.query_params.get('academic_year')
        if academic_year:
            filters['academic_year'] = int(academic_year)

        # Program
        program = request.query_params.get('program')
        if program:
            filters['program'] = int(program)

        # Class
        class_id = request.query_params.get('class')
        if class_id:
            filters['class'] = int(class_id)

        # Section
        section = request.query_params.get('section')
        if section:
            filters['section'] = int(section)

        # Department
        department = request.query_params.get('department')
        if department:
            filters['department'] = int(department)

        # Month and Year (for payroll)
        month = request.query_params.get('month')
        if month:
            filters['month'] = int(month)

        year = request.query_params.get('year')
        if year:
            filters['year'] = int(year)

        return filters

    def get_cache_key(self, prefix, college_id, filters):
        """Generate cache key based on prefix, college and filters"""
        return f"{prefix}:{college_id}:{hash(str(sorted(filters.items())))}"


@extend_schema_view(
    list=extend_schema(
        summary="Get Dashboard Overview Statistics",
        description="Returns comprehensive dashboard statistics including quick stats, today's attendance, financial summary, and recent activities",
        parameters=[],
        responses={200: DashboardStatsSerializer},
        tags=['Statistics - Dashboard']
    )
)
class DashboardStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for Dashboard Overview Statistics

    Provides a comprehensive overview of:
    - Quick stats (total students, teachers, staff, classes)
    - Today's attendance rates
    - Financial summary
    - Academic performance
    - Recent activities
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get dashboard overview statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('dashboard_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = DashboardStatsService(college_id, filters)
        stats_data = service.get_dashboard_overview()

        # Serialize response
        serializer = DashboardStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 5 minutes (dashboard updates frequently)
        cache.set(cache_key, response_data, 60 * 5)

        return Response(response_data)

    @extend_schema(
        summary="DEBUG: Check Database Data",
        description="Diagnostic endpoint to check what data exists in the database and which college ID to use",
        responses={200: dict},
        tags=['Statistics - Debug']
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def debug_data(self, request):
        """Debug endpoint to check database data"""
        # Get all colleges
        colleges = College.objects.all()

        result = {
            'total_colleges': colleges.count(),
            'colleges': []
        }

        for college in colleges:
            college_data = {
                'id': college.id,
                'name': college.name,
                'code': college.code,
                'data_summary': {
                    'students': Student.objects.filter(college_id=college.id).count(),
                    'teachers': Teacher.objects.filter(college_id=college.id).count(),
                    'users': User.objects.filter(college_id=college.id).count(),
                    'classes': Class.objects.filter(college_id=college.id).count(),
                }
            }
            result['colleges'].append(college_data)

        # Add overall totals
        result['overall_totals'] = {
            'total_students': Student.objects.all().count(),
            'total_teachers': Teacher.objects.all().count(),
            'total_users': User.objects.all().count(),
            'total_classes': Class.objects.all().count(),
        }

        if colleges.exists():
            result['message'] = "✅ Use X-College-ID header with one of the college IDs listed above"
        else:
            result['message'] = "❌ NO COLLEGES FOUND! Create colleges first in Django admin."

        return Response(result)


@extend_schema_view(
    list=extend_schema(
        summary="Get Academic Statistics",
        description="Returns comprehensive academic statistics including performance, attendance, assignments, and subject-wise analysis",
        parameters=[
            OpenApiParameter('from_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('to_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)'),
            OpenApiParameter('academic_year', OpenApiTypes.INT, description='Academic Year ID'),
            OpenApiParameter('program', OpenApiTypes.INT, description='Program ID'),
            OpenApiParameter('class', OpenApiTypes.INT, description='Class ID'),
            OpenApiParameter('section', OpenApiTypes.INT, description='Section ID'),
        ],
        responses={200: AcademicStatsSerializer},
        tags=['Statistics - Academic']
    )
)
class AcademicStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for Academic Statistics

    Provides endpoints for:
    - Student performance metrics
    - Attendance analytics
    - Assignment submission statistics
    - Subject-wise performance analysis
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get all academic statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('academic_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = AcademicStatsService(college_id, filters)
        stats_data = service.get_all_stats()

        # Serialize response
        serializer = AcademicStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)

        return Response(response_data)

    @extend_schema(
        summary="Get Performance Statistics Only",
        description="Returns only student performance metrics",
        responses={200: AcademicPerformanceStatsSerializer},
        tags=['Statistics - Academic']
    )
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """Get only performance statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = AcademicStatsService(college_id, filters)
        data = service.get_performance_stats()

        return Response(data)

    @extend_schema(
        summary="Get Attendance Statistics Only",
        description="Returns only attendance analytics",
        responses={200: AttendanceStatsSerializer},
        tags=['Statistics - Academic']
    )
    @action(detail=False, methods=['get'])
    def attendance(self, request):
        """Get only attendance statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = AcademicStatsService(college_id, filters)
        data = service.get_attendance_stats()

        return Response(data)

    @extend_schema(
        summary="Get Assignment Statistics Only",
        description="Returns only assignment submission statistics",
        responses={200: AssignmentStatsSerializer},
        tags=['Statistics - Academic']
    )
    @action(detail=False, methods=['get'])
    def assignments(self, request):
        """Get only assignment statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = AcademicStatsService(college_id, filters)
        data = service.get_assignment_stats()

        return Response(data)


@extend_schema_view(
    list=extend_schema(
        summary="Get Financial Statistics",
        description="Returns comprehensive financial statistics including fee collection, expenses, income, and net balance",
        parameters=[
            OpenApiParameter('from_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('to_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)'),
            OpenApiParameter('academic_year', OpenApiTypes.INT, description='Academic Year ID'),
            OpenApiParameter('program', OpenApiTypes.INT, description='Program ID'),
            OpenApiParameter('class', OpenApiTypes.INT, description='Class ID'),
        ],
        responses={200: FinancialStatsSerializer},
        tags=['Statistics - Financial']
    )
)
class FinancialStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for Financial Statistics

    Provides endpoints for:
    - Fee collection analytics
    - Expense breakdown
    - Income analysis
    - Net balance calculation
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get all financial statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('financial_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = FinancialStatsService(college_id, filters)
        stats_data = service.get_all_stats()

        # Serialize response
        serializer = FinancialStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)

        return Response(response_data)

    @extend_schema(
        summary="Get Fee Collection Statistics Only",
        description="Returns only fee collection analytics",
        responses={200: FeeCollectionStatsSerializer},
        tags=['Statistics - Financial']
    )
    @action(detail=False, methods=['get'])
    def fee_collection(self, request):
        """Get only fee collection statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = FinancialStatsService(college_id, filters)
        data = service.get_fee_collection_stats()

        return Response(data)

    @extend_schema(
        summary="Get Expense Statistics Only",
        description="Returns only expense breakdown",
        responses={200: ExpenseStatsSerializer},
        tags=['Statistics - Financial']
    )
    @action(detail=False, methods=['get'])
    def expenses(self, request):
        """Get only expense statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = FinancialStatsService(college_id, filters)
        data = service.get_expense_stats()

        return Response(data)

    @extend_schema(
        summary="Get Income Statistics Only",
        description="Returns only income analysis",
        responses={200: IncomeStatsSerializer},
        tags=['Statistics - Financial']
    )
    @action(detail=False, methods=['get'])
    def income(self, request):
        """Get only income statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = FinancialStatsService(college_id, filters)
        data = service.get_income_stats()

        return Response(data)


@extend_schema_view(
    list=extend_schema(
        summary="Get Library Statistics",
        description="Returns library circulation statistics including books, issues, returns, fines, and popular books",
        parameters=[
            OpenApiParameter('from_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('to_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)'),
        ],
        responses={200: LibraryCirculationStatsSerializer},
        tags=['Statistics - Library']
    )
)
class LibraryStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for Library Statistics

    Provides endpoints for:
    - Book circulation analytics
    - Fine collection statistics
    - Popular books analysis
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get library circulation statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('library_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = LibraryStatsService(college_id, filters)
        stats_data = service.get_circulation_stats()

        # Serialize response
        serializer = LibraryCirculationStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)

        return Response(response_data)


@extend_schema_view(
    list=extend_schema(
        summary="Get HR Statistics",
        description="Returns HR statistics including leave, payroll, and staff attendance",
        parameters=[
            OpenApiParameter('from_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('to_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)'),
            OpenApiParameter('department', OpenApiTypes.INT, description='Department ID'),
            OpenApiParameter('month', OpenApiTypes.INT, description='Month (1-12)'),
            OpenApiParameter('year', OpenApiTypes.INT, description='Year (YYYY)'),
        ],
        responses={200: HRStatsSerializer},
        tags=['Statistics - HR']
    )
)
class HRStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for HR Statistics

    Provides endpoints for:
    - Leave analytics
    - Payroll summary
    - Staff attendance statistics
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get all HR statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('hr_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = HRStatsService(college_id, filters)
        stats_data = service.get_all_stats()

        # Serialize response
        serializer = HRStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)

        return Response(response_data)


@extend_schema_view(
    list=extend_schema(
        summary="Get Store Sales Statistics",
        description="Returns store sales statistics including revenue, popular items, and payment methods",
        parameters=[
            OpenApiParameter('from_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('to_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)'),
        ],
        responses={200: StoreSalesStatsSerializer},
        tags=['Statistics - Store']
    )
)
class StoreStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for Store Statistics

    Provides endpoints for:
    - Sales analytics
    - Inventory statistics
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get store sales statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('store_sales_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = StoreStatsService(college_id, filters)
        stats_data = service.get_sales_stats()

        # Serialize response
        serializer = StoreSalesStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)

        return Response(response_data)

    @extend_schema(
        summary="Get Inventory Statistics",
        description="Returns inventory statistics including stock levels",
        responses={200: InventoryStatsSerializer},
        tags=['Statistics - Store']
    )
    @action(detail=False, methods=['get'])
    def inventory(self, request):
        """Get inventory statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = StoreStatsService(college_id, filters)
        data = service.get_inventory_stats()

        return Response(data)


@extend_schema_view(
    list=extend_schema(
        summary="Get Hostel Statistics",
        description="Returns hostel occupancy and fee statistics",
        parameters=[
            OpenApiParameter('from_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('to_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)'),
        ],
        responses={200: HostelOccupancyStatsSerializer},
        tags=['Statistics - Hostel']
    )
)
class HostelStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for Hostel Statistics

    Provides endpoints for:
    - Occupancy analytics
    - Hostel fee collection statistics
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get hostel occupancy statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('hostel_occupancy_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = HostelStatsService(college_id, filters)
        stats_data = service.get_occupancy_stats()

        # Serialize response
        serializer = HostelOccupancyStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)

        return Response(response_data)

    @extend_schema(
        summary="Get Hostel Fee Statistics",
        description="Returns hostel fee collection statistics",
        responses={200: HostelFeeStatsSerializer},
        tags=['Statistics - Hostel']
    )
    @action(detail=False, methods=['get'])
    def fees(self, request):
        """Get hostel fee statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        service = HostelStatsService(college_id, filters)
        data = service.get_fee_stats()

        return Response(data)


@extend_schema_view(
    list=extend_schema(
        summary="Get Communication Statistics",
        description="Returns communication statistics including messages and events",
        parameters=[
            OpenApiParameter('from_date', OpenApiTypes.DATE, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('to_date', OpenApiTypes.DATE, description='End date (YYYY-MM-DD)'),
        ],
        responses={200: CommunicationStatsSerializer},
        tags=['Statistics - Communication']
    )
)
class CommunicationStatsViewSet(CollegeScopedMixin, StatsFilterMixin, viewsets.ViewSet):
    """
    ViewSet for Communication Statistics

    Provides endpoints for:
    - Message delivery analytics
    - Event participation statistics
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get all communication statistics"""
        college_id = self.get_college_id()
        filters = self.parse_filters(request)

        # Create cache key
        cache_key = self.get_cache_key('communication_stats', college_id, filters)

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Calculate statistics
        service = CommunicationStatsService(college_id, filters)
        stats_data = service.get_all_stats()

        # Serialize response
        serializer = CommunicationStatsSerializer(stats_data)
        response_data = serializer.data

        # Cache for 15 minutes
        cache.set(cache_key, response_data, 60 * 15)

        return Response(response_data)
