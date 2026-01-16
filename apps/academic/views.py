"""
DRF ViewSets for Academic app with comprehensive API documentation.
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
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes
from apps.core.cache_mixins import CachedStaticMixin

from .models import (
    Faculty, Program, Class, Section, Subject, OptionalSubject,
    SubjectAssignment, Classroom, ClassTime, Timetable, LabSchedule, ClassTeacher
)
from .serializers import (
    FacultySerializer, FacultyListSerializer,
    ProgramSerializer, ProgramListSerializer,
    ClassSerializer, ClassListSerializer,
    SectionSerializer,
    SubjectSerializer, SubjectListSerializer,
    OptionalSubjectSerializer,
    SubjectAssignmentSerializer, SubjectAssignmentListSerializer,
    ClassroomSerializer, ClassroomListSerializer,
    ClassTimeSerializer,
    TimetableSerializer, TimetableListSerializer,
    LabScheduleSerializer,
    ClassTeacherSerializer,
    BulkDeleteSerializer,
)
from apps.core.mixins import CollegeScopedModelViewSet


# ============================================================================
# FACULTY VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all faculties",
        description="Retrieve a paginated list of all faculties in the current college.",
        parameters=[
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search by name or code'),
        ],
        responses={200: FacultyListSerializer(many=True)},
        tags=['Academic - Faculties']
    ),
    retrieve=extend_schema(
        summary="Get faculty details",
        responses={200: FacultySerializer},
        tags=['Academic - Faculties']
    ),
    create=extend_schema(
        summary="Create new faculty",
        request=FacultySerializer,
        responses={201: FacultySerializer},
        tags=['Academic - Faculties']
    ),
    update=extend_schema(
        summary="Update faculty",
        request=FacultySerializer,
        responses={200: FacultySerializer},
        tags=['Academic - Faculties']
    ),
    partial_update=extend_schema(
        summary="Partially update faculty",
        request=FacultySerializer,
        responses={200: FacultySerializer},
        tags=['Academic - Faculties']
    ),
    destroy=extend_schema(
        summary="Delete faculty",
        responses={204: None},
        tags=['Academic - Faculties']
    ),
)
class FacultyViewSet(CachedStaticMixin, CollegeScopedModelViewSet):
    """ViewSet for managing faculties/departments."""
    queryset = Faculty.objects.all_colleges()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'hod']
    search_fields = ['name', 'short_name', 'code']
    ordering_fields = ['name', 'code', 'display_order', 'created_at']
    ordering = ['display_order', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return FacultyListSerializer
        return FacultySerializer

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete."""
        instance.soft_delete()


# ============================================================================
# PROGRAM VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all programs",
        description="Retrieve all academic programs.",
        parameters=[
            OpenApiParameter(name='faculty', type=OpenApiTypes.INT, description='Filter by faculty ID'),
            OpenApiParameter(name='program_type', type=OpenApiTypes.STR, description='Filter by program type'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: ProgramListSerializer(many=True)},
        tags=['Academic - Programs']
    ),
    retrieve=extend_schema(
        summary="Get program details",
        responses={200: ProgramSerializer},
        tags=['Academic - Programs']
    ),
    create=extend_schema(
        summary="Create new program",
        request=ProgramSerializer,
        responses={201: ProgramSerializer},
        tags=['Academic - Programs']
    ),
    update=extend_schema(
        summary="Update program",
        request=ProgramSerializer,
        responses={200: ProgramSerializer},
        tags=['Academic - Programs']
    ),
    partial_update=extend_schema(
        summary="Partially update program",
        request=ProgramSerializer,
        responses={200: ProgramSerializer},
        tags=['Academic - Programs']
    ),
    destroy=extend_schema(
        summary="Delete program",
        responses={204: None},
        tags=['Academic - Programs']
    ),
)
class ProgramViewSet(CachedStaticMixin, CollegeScopedModelViewSet):
    """ViewSet for managing academic programs."""
    queryset = Program.objects.all_colleges()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['faculty', 'program_type', 'is_active']
    search_fields = ['name', 'short_name', 'code']
    ordering_fields = ['name', 'code', 'display_order', 'created_at']
    ordering = ['display_order', 'name']

    def get_queryset(self):
        """Default to active programs only for list action if filter not specified."""
        queryset = super().get_queryset()
        if self.action == 'list':
            is_active_param = self.request.query_params.get('is_active')
            if is_active_param is None:
                queryset = queryset.filter(is_active=True)
        return queryset


    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramListSerializer
        return ProgramSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# CLASS VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all classes",
        description="Retrieve classes for the current college.",
        parameters=[
            OpenApiParameter(name='program', type=OpenApiTypes.INT, description='Filter by program ID'),
            OpenApiParameter(name='academic_session', type=OpenApiTypes.INT, description='Filter by academic session ID'),
            OpenApiParameter(name='semester', type=OpenApiTypes.INT, description='Filter by semester'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: ClassListSerializer(many=True)},
        tags=['Academic - Classes']
    ),
    retrieve=extend_schema(
        summary="Get class details",
        responses={200: ClassSerializer},
        tags=['Academic - Classes']
    ),
    create=extend_schema(
        summary="Create new class",
        request=ClassSerializer,
        responses={201: ClassSerializer},
        tags=['Academic - Classes']
    ),
    update=extend_schema(
        summary="Update class",
        request=ClassSerializer,
        responses={200: ClassSerializer},
        tags=['Academic - Classes']
    ),
    partial_update=extend_schema(
        summary="Partially update class",
        request=ClassSerializer,
        responses={200: ClassSerializer},
        tags=['Academic - Classes']
    ),
    destroy=extend_schema(
        summary="Delete class",
        responses={204: None},
        tags=['Academic - Classes']
    ),
)
class ClassViewSet(CachedStaticMixin, CollegeScopedModelViewSet):
    """ViewSet for managing classes."""
    queryset = Class.objects.all_colleges()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'academic_session', 'semester', 'year', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'semester', 'created_at']
    ordering = ['semester', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassListSerializer
        return ClassSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# SECTION VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all sections",
        description="Retrieve sections for classes.",
        parameters=[
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: SectionSerializer(many=True)},
        tags=['Academic - Sections']
    ),
    retrieve=extend_schema(
        summary="Get section details",
        responses={200: SectionSerializer},
        tags=['Academic - Sections']
    ),
    create=extend_schema(
        summary="Create new section",
        request=SectionSerializer,
        responses={201: SectionSerializer},
        tags=['Academic - Sections']
    ),
    update=extend_schema(
        summary="Update section",
        request=SectionSerializer,
        responses={200: SectionSerializer},
        tags=['Academic - Sections']
    ),
    partial_update=extend_schema(
        summary="Partially update section",
        request=SectionSerializer,
        responses={200: SectionSerializer},
        tags=['Academic - Sections']
    ),
    destroy=extend_schema(
        summary="Delete section",
        responses={204: None},
        tags=['Academic - Sections']
    ),
)
class SectionViewSet(CachedStaticMixin, CollegeScopedModelViewSet):
    """ViewSet for managing sections."""
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Override to filter sections by college through class_obj relationship."""
        queryset = Section.objects.all()
        college_id = self.get_college_id(required=False)

        # Check if college_id is 'all' (superuser/staff global view)
        if college_id == 'all':
            return queryset

        # Superusers/staff without any header also get all records
        user = getattr(self.request, 'user', None)
        if user and (user.is_superuser or user.is_staff) and not college_id:
            return queryset

        # Regular users need a valid college_id
        if not college_id:
            college_id = self.get_college_id(required=True)

        # Filter sections by college through class_obj relationship
        return queryset.filter(class_obj__college_id=college_id)

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# SUBJECT VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List all subjects",
        description="Retrieve subjects for the current college.",
        parameters=[
            OpenApiParameter(name='subject_type', type=OpenApiTypes.STR, description='Filter by subject type'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: SubjectListSerializer(many=True)},
        tags=['Academic - Subjects']
    ),
    retrieve=extend_schema(
        summary="Get subject details",
        responses={200: SubjectSerializer},
        tags=['Academic - Subjects']
    ),
    create=extend_schema(
        summary="Create new subject",
        request=SubjectSerializer,
        responses={201: SubjectSerializer},
        tags=['Academic - Subjects']
    ),
    update=extend_schema(
        summary="Update subject",
        request=SubjectSerializer,
        responses={200: SubjectSerializer},
        tags=['Academic - Subjects']
    ),
    partial_update=extend_schema(
        summary="Partially update subject",
        request=SubjectSerializer,
        responses={200: SubjectSerializer},
        tags=['Academic - Subjects']
    ),
    destroy=extend_schema(
        summary="Delete subject",
        responses={204: None},
        tags=['Academic - Subjects']
    ),
)
class SubjectViewSet(CachedStaticMixin, CollegeScopedModelViewSet):
    """ViewSet for managing subjects."""
    queryset = Subject.objects.all_colleges()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject_type', 'is_active']
    search_fields = ['name', 'short_name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectListSerializer
        return SubjectSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# OPTIONAL SUBJECT VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List optional subject groups",
        description="Retrieve optional subject groups.",
        parameters=[
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: OptionalSubjectSerializer(many=True)},
        tags=['Academic - Optional Subjects']
    ),
    retrieve=extend_schema(
        summary="Get optional subject group details",
        responses={200: OptionalSubjectSerializer},
        tags=['Academic - Optional Subjects']
    ),
    create=extend_schema(
        summary="Create optional subject group",
        request=OptionalSubjectSerializer,
        responses={201: OptionalSubjectSerializer},
        tags=['Academic - Optional Subjects']
    ),
    update=extend_schema(
        summary="Update optional subject group",
        request=OptionalSubjectSerializer,
        responses={200: OptionalSubjectSerializer},
        tags=['Academic - Optional Subjects']
    ),
    partial_update=extend_schema(
        summary="Partially update optional subject group",
        request=OptionalSubjectSerializer,
        responses={200: OptionalSubjectSerializer},
        tags=['Academic - Optional Subjects']
    ),
    destroy=extend_schema(
        summary="Delete optional subject group",
        responses={204: None},
        tags=['Academic - Optional Subjects']
    ),
)
class OptionalSubjectViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing optional subject groups."""
    queryset = OptionalSubject.objects.all()
    serializer_class = OptionalSubjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """Override to filter optional subjects by college through class_obj relationship."""
        queryset = OptionalSubject.objects.all()
        college_id = self.get_college_id(required=False)

        if college_id == 'all':
            return queryset

        user = getattr(self.request, 'user', None)
        if user and (user.is_superuser or user.is_staff) and not college_id:
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        return queryset.filter(class_obj__college_id=college_id)

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# SUBJECT ASSIGNMENT VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List subject assignments",
        description="Retrieve subject assignments.",
        parameters=[
            OpenApiParameter(name='subject', type=OpenApiTypes.INT, description='Filter by subject ID'),
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='teacher', type=OpenApiTypes.STR, description='Filter by teacher ID'),
            OpenApiParameter(name='is_optional', type=OpenApiTypes.BOOL, description='Filter by optional flag'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: SubjectAssignmentListSerializer(many=True)},
        tags=['Academic - Subject Assignments']
    ),
    retrieve=extend_schema(
        summary="Get subject assignment details",
        responses={200: SubjectAssignmentSerializer},
        tags=['Academic - Subject Assignments']
    ),
    create=extend_schema(
        summary="Create subject assignment",
        request=SubjectAssignmentSerializer,
        responses={201: SubjectAssignmentSerializer},
        tags=['Academic - Subject Assignments']
    ),
    update=extend_schema(
        summary="Update subject assignment",
        request=SubjectAssignmentSerializer,
        responses={200: SubjectAssignmentSerializer},
        tags=['Academic - Subject Assignments']
    ),
    partial_update=extend_schema(
        summary="Partially update subject assignment",
        request=SubjectAssignmentSerializer,
        responses={200: SubjectAssignmentSerializer},
        tags=['Academic - Subject Assignments']
    ),
    destroy=extend_schema(
        summary="Delete subject assignment",
        responses={204: None},
        tags=['Academic - Subject Assignments']
    ),
)
class SubjectAssignmentViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing subject assignments."""
    queryset = SubjectAssignment.objects.all()
    serializer_class = SubjectAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'class_obj', 'section', 'teacher', 'is_optional', 'is_active']
    search_fields = ['subject__name', 'teacher__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Override to filter subject assignments by college through class_obj relationship."""
        queryset = SubjectAssignment.objects.all()
        college_id = self.get_college_id(required=False)

        if college_id == 'all':
            return queryset

        user = getattr(self.request, 'user', None)
        if user and (user.is_superuser or user.is_staff) and not college_id:
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        return queryset.filter(class_obj__college_id=college_id)

    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectAssignmentListSerializer
        return SubjectAssignmentSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# CLASSROOM VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List classrooms",
        description="Retrieve classrooms for the current college.",
        parameters=[
            OpenApiParameter(name='room_type', type=OpenApiTypes.STR, description='Filter by room type'),
            OpenApiParameter(name='building', type=OpenApiTypes.STR, description='Filter by building'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: ClassroomListSerializer(many=True)},
        tags=['Academic - Classrooms']
    ),
    retrieve=extend_schema(
        summary="Get classroom details",
        responses={200: ClassroomSerializer},
        tags=['Academic - Classrooms']
    ),
    create=extend_schema(
        summary="Create new classroom",
        request=ClassroomSerializer,
        responses={201: ClassroomSerializer},
        tags=['Academic - Classrooms']
    ),
    update=extend_schema(
        summary="Update classroom",
        request=ClassroomSerializer,
        responses={200: ClassroomSerializer},
        tags=['Academic - Classrooms']
    ),
    partial_update=extend_schema(
        summary="Partially update classroom",
        request=ClassroomSerializer,
        responses={200: ClassroomSerializer},
        tags=['Academic - Classrooms']
    ),
    destroy=extend_schema(
        summary="Delete classroom",
        responses={204: None},
        tags=['Academic - Classrooms']
    ),
)
class ClassroomViewSet(CachedStaticMixin, CollegeScopedModelViewSet):
    """ViewSet for managing classrooms."""
    queryset = Classroom.objects.all_colleges()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type', 'building', 'has_projector', 'has_ac', 'has_computer', 'is_active']
    search_fields = ['name', 'code', 'building']
    ordering_fields = ['name', 'code', 'capacity', 'created_at']
    ordering = ['building', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClassroomListSerializer
        return ClassroomSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# CLASS TIME VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List class times",
        description="Retrieve class time slots for the current college.",
        parameters=[
            OpenApiParameter(name='is_break', type=OpenApiTypes.BOOL, description='Filter by break flag'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: ClassTimeSerializer(many=True)},
        tags=['Academic - Class Times']
    ),
    retrieve=extend_schema(
        summary="Get class time details",
        responses={200: ClassTimeSerializer},
        tags=['Academic - Class Times']
    ),
    create=extend_schema(
        summary="Create class time",
        request=ClassTimeSerializer,
        responses={201: ClassTimeSerializer},
        tags=['Academic - Class Times']
    ),
    update=extend_schema(
        summary="Update class time",
        request=ClassTimeSerializer,
        responses={200: ClassTimeSerializer},
        tags=['Academic - Class Times']
    ),
    partial_update=extend_schema(
        summary="Partially update class time",
        request=ClassTimeSerializer,
        responses={200: ClassTimeSerializer},
        tags=['Academic - Class Times']
    ),
    destroy=extend_schema(
        summary="Delete class time",
        responses={204: None},
        tags=['Academic - Class Times']
    ),
)
class ClassTimeViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing class time slots."""
    queryset = ClassTime.objects.all_colleges()
    serializer_class = ClassTimeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_break', 'is_active']
    ordering_fields = ['period_number', 'start_time']
    ordering = ['period_number']


    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        timetable_filters = {}

        class_obj = params.get('class_obj')
        section = params.get('section')
        day_of_week = params.get('day_of_week')
        timetable_is_active = params.get('timetable_is_active')
        if timetable_is_active is None and (class_obj or section or day_of_week):
            timetable_is_active = params.get('is_active')

        if class_obj:
            timetable_filters['timetable_entries__class_obj_id'] = class_obj
        if section:
            timetable_filters['timetable_entries__section_id'] = section
        if day_of_week:
            timetable_filters['timetable_entries__day_of_week'] = day_of_week
        if timetable_is_active is not None:
            if str(timetable_is_active).lower() in ['true', '1', 'yes']:
                timetable_filters['timetable_entries__is_active'] = True
            elif str(timetable_is_active).lower() in ['false', '0', 'no']:
                timetable_filters['timetable_entries__is_active'] = False

        if timetable_filters:
            qs = qs.filter(**timetable_filters).distinct()

        return qs

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# TIMETABLE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List timetable entries",
        description="Retrieve timetable entries.",
        parameters=[
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='day_of_week', type=OpenApiTypes.INT, description='Filter by day of week (0-6)'),
            OpenApiParameter(name='classroom', type=OpenApiTypes.INT, description='Filter by classroom ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: TimetableListSerializer(many=True)},
        tags=['Academic - Timetable']
    ),
    retrieve=extend_schema(
        summary="Get timetable entry details",
        responses={200: TimetableSerializer},
        tags=['Academic - Timetable']
    ),
    create=extend_schema(
        summary="Create timetable entry",
        request=TimetableSerializer,
        responses={201: TimetableSerializer},
        tags=['Academic - Timetable']
    ),
    update=extend_schema(
        summary="Update timetable entry",
        request=TimetableSerializer,
        responses={200: TimetableSerializer},
        tags=['Academic - Timetable']
    ),
    partial_update=extend_schema(
        summary="Partially update timetable entry",
        request=TimetableSerializer,
        responses={200: TimetableSerializer},
        tags=['Academic - Timetable']
    ),
    destroy=extend_schema(
        summary="Delete timetable entry",
        responses={204: None},
        tags=['Academic - Timetable']
    ),
)
class TimetableViewSet(CachedStaticMixin, CollegeScopedModelViewSet):
    """ViewSet for managing timetable entries."""
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['section', 'day_of_week', 'class_time', 'classroom', 'is_active']
    ordering_fields = ['day_of_week', 'class_time', 'created_at']
    ordering = ['day_of_week', 'class_time__period_number']

    def get_queryset(self):
        """Override to filter timetables by college through class_obj relationship."""
        queryset = Timetable.objects.all()
        college_id = self.get_college_id(required=False)

        if college_id == 'all':
            return queryset

        user = getattr(self.request, 'user', None)
        if user and (user.is_superuser or user.is_staff) and not college_id:
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        return queryset.filter(class_obj__college_id=college_id)

    def get_serializer_class(self):
        if self.action == 'list':
            return TimetableListSerializer
        return TimetableSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# LAB SCHEDULE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List lab schedules",
        description="Retrieve lab schedules.",
        parameters=[
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='subject_assignment', type=OpenApiTypes.INT, description='Filter by subject assignment ID'),
            OpenApiParameter(name='day_of_week', type=OpenApiTypes.INT, description='Filter by day of week (0-6)'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: LabScheduleSerializer(many=True)},
        tags=['Academic - Lab Schedules']
    ),
    retrieve=extend_schema(
        summary="Get lab schedule details",
        responses={200: LabScheduleSerializer},
        tags=['Academic - Lab Schedules']
    ),
    create=extend_schema(
        summary="Create lab schedule",
        request=LabScheduleSerializer,
        responses={201: LabScheduleSerializer},
        tags=['Academic - Lab Schedules']
    ),
    update=extend_schema(
        summary="Update lab schedule",
        request=LabScheduleSerializer,
        responses={200: LabScheduleSerializer},
        tags=['Academic - Lab Schedules']
    ),
    partial_update=extend_schema(
        summary="Partially update lab schedule",
        request=LabScheduleSerializer,
        responses={200: LabScheduleSerializer},
        tags=['Academic - Lab Schedules']
    ),
    destroy=extend_schema(
        summary="Delete lab schedule",
        responses={204: None},
        tags=['Academic - Lab Schedules']
    ),
)
class LabScheduleViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing lab schedules."""
    queryset = LabSchedule.objects.all()
    serializer_class = LabScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['subject_assignment', 'section', 'day_of_week', 'classroom', 'is_active']
    ordering_fields = ['day_of_week', 'start_time', 'created_at']
    ordering = ['day_of_week', 'start_time']

    def get_queryset(self):
        """Override to filter lab schedules by college through section's class_obj relationship."""
        queryset = LabSchedule.objects.all()
        college_id = self.get_college_id(required=False)

        if college_id == 'all':
            return queryset

        user = getattr(self.request, 'user', None)
        if user and (user.is_superuser or user.is_staff) and not college_id:
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        return queryset.filter(section__class_obj__college_id=college_id)

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# CLASS TEACHER VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List class teachers",
        description="Retrieve class teacher assignments.",
        parameters=[
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='teacher', type=OpenApiTypes.STR, description='Filter by teacher ID'),
            OpenApiParameter(name='is_current', type=OpenApiTypes.BOOL, description='Filter by current flag'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: ClassTeacherSerializer(many=True)},
        tags=['Academic - Class Teachers']
    ),
    retrieve=extend_schema(
        summary="Get class teacher details",
        responses={200: ClassTeacherSerializer},
        tags=['Academic - Class Teachers']
    ),
    create=extend_schema(
        summary="Assign class teacher",
        request=ClassTeacherSerializer,
        responses={201: ClassTeacherSerializer},
        tags=['Academic - Class Teachers']
    ),
    update=extend_schema(
        summary="Update class teacher",
        request=ClassTeacherSerializer,
        responses={200: ClassTeacherSerializer},
        tags=['Academic - Class Teachers']
    ),
    partial_update=extend_schema(
        summary="Partially update class teacher",
        request=ClassTeacherSerializer,
        responses={200: ClassTeacherSerializer},
        tags=['Academic - Class Teachers']
    ),
    destroy=extend_schema(
        summary="Delete class teacher",
        responses={204: None},
        tags=['Academic - Class Teachers']
    ),
)
class ClassTeacherViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing class teacher assignments."""
    queryset = ClassTeacher.objects.all()
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'section', 'teacher', 'is_current', 'is_active']
    ordering_fields = ['assigned_from', 'created_at']
    ordering = ['-assigned_from']

    def get_queryset(self):
        """Override to filter class teachers by college through class_obj relationship."""
        queryset = ClassTeacher.objects.all()
        college_id = self.get_college_id(required=False)

        if college_id == 'all':
            return queryset

        user = getattr(self.request, 'user', None)
        if user and (user.is_superuser or user.is_staff) and not college_id:
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        return queryset.filter(class_obj__college_id=college_id)

    def perform_destroy(self, instance):
        instance.soft_delete()
