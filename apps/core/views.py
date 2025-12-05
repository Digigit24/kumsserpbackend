"""
DRF ViewSets for Core app with comprehensive API documentation.
"""
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from .models import (
    College,
    AcademicYear,
    AcademicSession,
    Holiday,
    Weekend,
    SystemSetting,
    NotificationSetting,
    ActivityLog
)
from .serializers import (
    CollegeSerializer,
    CollegeListSerializer,
    CollegeCreateSerializer,
    AcademicYearSerializer,
    AcademicSessionSerializer,
    HolidaySerializer,
    WeekendSerializer,
    SystemSettingSerializer,
    NotificationSettingSerializer,
    ActivityLogSerializer,
    BulkDeleteSerializer,
    BulkActivateSerializer,
)
from .mixins import CollegeScopedModelViewSet, CollegeScopedReadOnlyModelViewSet


# ============================================================================
# COLLEGE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all colleges",
        description="Retrieve a paginated list of all colleges in the current tenant.",
        parameters=[
            OpenApiParameter(
                name='X-College-ID',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                description='College identifier (legacy: X-Tenant-ID)',
                required=True
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='is_main',
                type=OpenApiTypes.BOOL,
                description='Filter main university'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search by name, code, or city'
            ),
        ],
        responses={200: CollegeListSerializer(many=True)},
        tags=['Colleges']
    ),
    retrieve=extend_schema(
        summary="Get college details",
        description="Retrieve detailed information about a specific college.",
        responses={200: CollegeSerializer},
        tags=['Colleges']
    ),
    create=extend_schema(
        summary="Create new college",
        description="Create a new college. Automatically creates default notification settings and weekend configuration.",
        request=CollegeCreateSerializer,
        responses={201: CollegeSerializer},
        tags=['Colleges']
    ),
    update=extend_schema(
        summary="Update college",
        description="Update all fields of a college.",
        request=CollegeSerializer,
        responses={200: CollegeSerializer},
        tags=['Colleges']
    ),
    partial_update=extend_schema(
        summary="Partially update college",
        description="Update specific fields of a college.",
        request=CollegeSerializer,
        responses={200: CollegeSerializer},
        tags=['Colleges']
    ),
    destroy=extend_schema(
        summary="Delete college",
        description="Soft delete a college (sets is_active=False).",
        responses={204: None},
        tags=['Colleges']
    ),
)
class CollegeViewSet(CollegeScopedModelViewSet):
    """
    ViewSet for managing colleges in the college-scoped system.

    Provides CRUD operations and custom actions for college management.
    """
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_main', 'state', 'country']
    search_fields = ['name', 'short_name', 'code', 'city', 'email']
    ordering_fields = ['name', 'code', 'display_order', 'created_at']
    ordering = ['display_order', 'name']

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return CollegeListSerializer
        if self.action == 'create':
            return CollegeCreateSerializer
        return CollegeSerializer

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()

    @extend_schema(
        summary="Bulk delete colleges",
        description="Soft delete multiple colleges at once.",
        request=BulkDeleteSerializer,
        responses={200: OpenApiResponse(description="Colleges deleted successfully")},
        tags=['Colleges']
    )
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Soft delete multiple colleges."""
        serializer = BulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data['ids']
        colleges = self.get_queryset().filter(id__in=ids)
        count = colleges.count()

        for college in colleges:
            college.soft_delete()

        return Response({
            'message': f'{count} colleges deleted successfully',
            'deleted_ids': ids
        })

    @extend_schema(
        summary="Get active colleges",
        description="Retrieve only active colleges.",
        responses={200: CollegeListSerializer(many=True)},
        tags=['Colleges']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active colleges."""
        colleges = self.get_queryset().filter(is_active=True)
        serializer = CollegeListSerializer(colleges, many=True)
        return Response(serializer.data)


# ============================================================================
# ACADEMIC YEAR VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List academic years",
        description="Retrieve all academic years for the current college context.",
        parameters=[
            OpenApiParameter(
                name='is_current',
                type=OpenApiTypes.BOOL,
                description='Filter current academic year'
            ),
        ],
        responses={200: AcademicYearSerializer(many=True)},
        tags=['Academic Years']
    ),
    retrieve=extend_schema(
        summary="Get academic year details",
        responses={200: AcademicYearSerializer},
        tags=['Academic Years']
    ),
    create=extend_schema(
        summary="Create academic year",
        description="Create a new academic year. If is_current=True, automatically sets other years to is_current=False.",
        request=AcademicYearSerializer,
        responses={201: AcademicYearSerializer},
        tags=['Academic Years']
    ),
    update=extend_schema(
        summary="Update academic year",
        request=AcademicYearSerializer,
        responses={200: AcademicYearSerializer},
        tags=['Academic Years']
    ),
    partial_update=extend_schema(
        summary="Partially update academic year",
        request=AcademicYearSerializer,
        responses={200: AcademicYearSerializer},
        tags=['Academic Years']
    ),
    destroy=extend_schema(
        summary="Delete academic year",
        responses={204: None},
        tags=['Academic Years']
    ),
)
class AcademicYearViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing academic years."""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_current', 'is_active']
    search_fields = ['year']
    ordering_fields = ['start_date', 'year']
    ordering = ['-start_date']

    @extend_schema(
        summary="Get current academic year",
        description="Retrieve the currently active academic year.",
        responses={200: AcademicYearSerializer},
        tags=['Academic Years']
    )
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get the current academic year."""
        try:
            current_year = self.get_queryset().get(is_current=True, is_active=True)
            serializer = self.get_serializer(current_year)
            return Response(serializer.data)
        except AcademicYear.DoesNotExist:
            return Response(
                {'error': 'No current academic year found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# ACADEMIC SESSION VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List academic sessions",
        description="Retrieve all academic sessions.",
        parameters=[
            OpenApiParameter(name='college', type=OpenApiTypes.INT, description='Filter by college ID'),
            OpenApiParameter(name='academic_year', type=OpenApiTypes.INT, description='Filter by academic year ID'),
            OpenApiParameter(name='semester', type=OpenApiTypes.INT, description='Filter by semester'),
            OpenApiParameter(name='is_current', type=OpenApiTypes.BOOL, description='Filter current session'),
        ],
        responses={200: AcademicSessionSerializer(many=True)},
        tags=['Academic Sessions']
    ),
    retrieve=extend_schema(
        summary="Get session details",
        responses={200: AcademicSessionSerializer},
        tags=['Academic Sessions']
    ),
    create=extend_schema(
        summary="Create academic session",
        request=AcademicSessionSerializer,
        responses={201: AcademicSessionSerializer},
        tags=['Academic Sessions']
    ),
    update=extend_schema(
        summary="Update session",
        request=AcademicSessionSerializer,
        responses={200: AcademicSessionSerializer},
        tags=['Academic Sessions']
    ),
    partial_update=extend_schema(
        summary="Partially update session",
        request=AcademicSessionSerializer,
        responses={200: AcademicSessionSerializer},
        tags=['Academic Sessions']
    ),
    destroy=extend_schema(
        summary="Delete session",
        responses={204: None},
        tags=['Academic Sessions']
    ),
)
class AcademicSessionViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing academic sessions (semesters)."""
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'academic_year', 'semester', 'is_current', 'is_active']
    search_fields = ['name']
    ordering_fields = ['start_date', 'semester']
    ordering = ['-start_date']


# ============================================================================
# HOLIDAY VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List holidays",
        description="Retrieve holidays for colleges.",
        parameters=[
            OpenApiParameter(name='college', type=OpenApiTypes.INT, description='Filter by college ID'),
            OpenApiParameter(name='holiday_type', type=OpenApiTypes.STR, description='Filter by holiday type'),
            OpenApiParameter(name='date', type=OpenApiTypes.DATE, description='Filter by date'),
        ],
        responses={200: HolidaySerializer(many=True)},
        tags=['Holidays']
    ),
    retrieve=extend_schema(
        summary="Get holiday details",
        responses={200: HolidaySerializer},
        tags=['Holidays']
    ),
    create=extend_schema(
        summary="Create holiday",
        request=HolidaySerializer,
        responses={201: HolidaySerializer},
        tags=['Holidays']
    ),
    update=extend_schema(
        summary="Update holiday",
        request=HolidaySerializer,
        responses={200: HolidaySerializer},
        tags=['Holidays']
    ),
    partial_update=extend_schema(
        summary="Partially update holiday",
        request=HolidaySerializer,
        responses={200: HolidaySerializer},
        tags=['Holidays']
    ),
    destroy=extend_schema(
        summary="Delete holiday",
        responses={204: None},
        tags=['Holidays']
    ),
)
class HolidayViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing holidays."""
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'holiday_type', 'date', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['date', 'name']
    ordering = ['date']


# ============================================================================
# WEEKEND VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List weekend configurations",
        description="Retrieve weekend day configurations for colleges.",
        parameters=[
            OpenApiParameter(name='college', type=OpenApiTypes.INT, description='Filter by college ID'),
        ],
        responses={200: WeekendSerializer(many=True)},
        tags=['Weekends']
    ),
    retrieve=extend_schema(
        summary="Get weekend details",
        responses={200: WeekendSerializer},
        tags=['Weekends']
    ),
    create=extend_schema(
        summary="Create weekend configuration",
        request=WeekendSerializer,
        responses={201: WeekendSerializer},
        tags=['Weekends']
    ),
    update=extend_schema(
        summary="Update weekend",
        request=WeekendSerializer,
        responses={200: WeekendSerializer},
        tags=['Weekends']
    ),
    partial_update=extend_schema(
        summary="Partially update weekend",
        request=WeekendSerializer,
        responses={200: WeekendSerializer},
        tags=['Weekends']
    ),
    destroy=extend_schema(
        summary="Delete weekend",
        responses={204: None},
        tags=['Weekends']
    ),
)
class WeekendViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing weekend configurations."""
    queryset = Weekend.objects.all()
    serializer_class = WeekendSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['college', 'day', 'is_active']
    ordering_fields = ['day']
    ordering = ['day']


# ============================================================================
# SYSTEM SETTING VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List system settings",
        responses={200: SystemSettingSerializer(many=True)},
        tags=['System Settings']
    ),
    retrieve=extend_schema(
        summary="Get system settings",
        responses={200: SystemSettingSerializer},
        tags=['System Settings']
    ),
    create=extend_schema(
        summary="Create system settings",
        request=SystemSettingSerializer,
        responses={201: SystemSettingSerializer},
        tags=['System Settings']
    ),
    update=extend_schema(
        summary="Update system settings",
        request=SystemSettingSerializer,
        responses={200: SystemSettingSerializer},
        tags=['System Settings']
    ),
    partial_update=extend_schema(
        summary="Partially update system settings",
        request=SystemSettingSerializer,
        responses={200: SystemSettingSerializer},
        tags=['System Settings']
    ),
)
class SystemSettingViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing system-wide settings."""
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    http_method_names = ['get', 'post', 'put', 'patch']  # No DELETE


# ============================================================================
# NOTIFICATION SETTING VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List notification settings",
        parameters=[
            OpenApiParameter(name='college', type=OpenApiTypes.INT, description='Filter by college ID'),
        ],
        responses={200: NotificationSettingSerializer(many=True)},
        tags=['Notification Settings']
    ),
    retrieve=extend_schema(
        summary="Get notification settings",
        responses={200: NotificationSettingSerializer},
        tags=['Notification Settings']
    ),
    create=extend_schema(
        summary="Create notification settings",
        request=NotificationSettingSerializer,
        responses={201: NotificationSettingSerializer},
        tags=['Notification Settings']
    ),
    update=extend_schema(
        summary="Update notification settings",
        request=NotificationSettingSerializer,
        responses={200: NotificationSettingSerializer},
        tags=['Notification Settings']
    ),
    partial_update=extend_schema(
        summary="Partially update notification settings",
        request=NotificationSettingSerializer,
        responses={200: NotificationSettingSerializer},
        tags=['Notification Settings']
    ),
)
class NotificationSettingViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing notification configurations."""
    queryset = NotificationSetting.objects.all()
    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['college', 'is_active']
    http_method_names = ['get', 'post', 'put', 'patch']  # No DELETE


# ============================================================================
# ACTIVITY LOG VIEWSET (Read-Only)
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List activity logs",
        description="Retrieve audit trail of system activities (read-only).",
        parameters=[
            OpenApiParameter(name='user', type=OpenApiTypes.INT, description='Filter by user ID'),
            OpenApiParameter(name='college', type=OpenApiTypes.INT, description='Filter by college ID'),
            OpenApiParameter(name='action', type=OpenApiTypes.STR, description='Filter by action type'),
            OpenApiParameter(name='model_name', type=OpenApiTypes.STR, description='Filter by model name'),
        ],
        responses={200: ActivityLogSerializer(many=True)},
        tags=['Activity Logs']
    ),
    retrieve=extend_schema(
        summary="Get activity log details",
        responses={200: ActivityLogSerializer},
        tags=['Activity Logs']
    ),
)
class ActivityLogViewSet(CollegeScopedReadOnlyModelViewSet):
    """Read-only ViewSet for viewing activity logs."""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'college', 'action', 'model_name']
    search_fields = ['description', 'object_id', 'user__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
