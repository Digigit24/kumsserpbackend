"""
DRF ViewSets for Teachers app with comprehensive API documentation.
"""
from apps.core.cache_mixins import CachedReadOnlyMixin
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

from .models import (
    Teacher, StudyMaterial, Assignment, AssignmentSubmission,
    Homework, HomeworkSubmission
)
from .serializers import (
    TeacherSerializer, TeacherListSerializer,
    StudyMaterialSerializer, StudyMaterialListSerializer,
    AssignmentSerializer, AssignmentListSerializer,
    AssignmentSubmissionSerializer, AssignmentSubmissionListSerializer,
    HomeworkSerializer, HomeworkListSerializer,
    HomeworkSubmissionSerializer,
    BulkDeleteSerializer,
)
from apps.core.mixins import CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet


# ============================================================================
# TEACHER VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List teachers",
        description="Retrieve teachers for the current college.",
        parameters=[
            OpenApiParameter(name='faculty', type=OpenApiTypes.INT, description='Filter by faculty ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search by name, employee ID, email'),
        ],
        responses={200: TeacherListSerializer(many=True)},
        tags=['Teachers']
    ),
    retrieve=extend_schema(
        summary="Get teacher details",
        responses={200: TeacherSerializer},
        tags=['Teachers']
    ),
    create=extend_schema(
        summary="Create teacher",
        request=TeacherSerializer,
        responses={201: TeacherSerializer},
        tags=['Teachers']
    ),
    update=extend_schema(
        summary="Update teacher",
        request=TeacherSerializer,
        responses={200: TeacherSerializer},
        tags=['Teachers']
    ),
    partial_update=extend_schema(
        summary="Partially update teacher",
        request=TeacherSerializer,
        responses={200: TeacherSerializer},
        tags=['Teachers']
    ),
    destroy=extend_schema(
        summary="Delete teacher",
        responses={204: None},
        tags=['Teachers']
    ),
)
class TeacherViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    """ViewSet for managing teachers."""
    queryset = Teacher.objects.all_colleges()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['faculty', 'is_active', 'gender']
    search_fields = ['first_name', 'last_name', 'employee_id', 'email', 'phone']
    ordering_fields = ['employee_id', 'first_name', 'joining_date', 'created_at']
    ordering = ['employee_id']

    def get_serializer_class(self):
        if self.action == 'list':
            return TeacherListSerializer
        return TeacherSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()

    @extend_schema(
        summary="Get current teacher profile",
        description="Get the teacher profile for the currently logged-in user. Returns 404 if user is not a teacher.",
        responses={
            200: TeacherSerializer,
            404: OpenApiResponse(description="User is not a teacher or teacher profile not found")
        },
        tags=['Teachers']
    )
    @action(detail=False, methods=['get'], url_path='me')
    def current_teacher(self, request):
        """Get the teacher profile for the currently logged-in user."""
        try:
            teacher = Teacher.objects.all_colleges().get(
                user=request.user,
                is_active=True
            )
            serializer = self.get_serializer(teacher)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response(
                {
                    'error': 'Teacher profile not found',
                    'detail': 'The current user does not have an active teacher profile.'
                },
                status=status.HTTP_404_NOT_FOUND
            )


# ============================================================================
# STUDY MATERIAL VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List study materials",
        description="Retrieve study materials.",
        parameters=[
            OpenApiParameter(name='teacher', type=OpenApiTypes.INT, description='Filter by teacher ID'),
            OpenApiParameter(name='subject', type=OpenApiTypes.INT, description='Filter by subject ID'),
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='content_type', type=OpenApiTypes.STR, description='Filter by content type'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: StudyMaterialListSerializer(many=True)},
        tags=['Teachers - Study Materials']
    ),
    retrieve=extend_schema(
        summary="Get study material details",
        responses={200: StudyMaterialSerializer},
        tags=['Teachers - Study Materials']
    ),
    create=extend_schema(
        summary="Upload study material",
        request=StudyMaterialSerializer,
        responses={201: StudyMaterialSerializer},
        tags=['Teachers - Study Materials']
    ),
    update=extend_schema(
        summary="Update study material",
        request=StudyMaterialSerializer,
        responses={200: StudyMaterialSerializer},
        tags=['Teachers - Study Materials']
    ),
    partial_update=extend_schema(
        summary="Partially update study material",
        request=StudyMaterialSerializer,
        responses={200: StudyMaterialSerializer},
        tags=['Teachers - Study Materials']
    ),
    destroy=extend_schema(
        summary="Delete study material",
        responses={204: None},
        tags=['Teachers - Study Materials']
    ),
)
class StudyMaterialViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing study materials."""
    queryset = StudyMaterial.objects.all_colleges()
    serializer_class = StudyMaterialSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'subject', 'class_obj', 'section', 'content_type', 'is_active']
    search_fields = ['title', 'description', 'topic', 'tags']
    ordering_fields = ['upload_date', 'view_count', 'created_at']
    ordering = ['-upload_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudyMaterialListSerializer
        return StudyMaterialSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# ASSIGNMENT VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List assignments",
        description="Retrieve assignments.",
        parameters=[
            OpenApiParameter(name='teacher', type=OpenApiTypes.INT, description='Filter by teacher ID'),
            OpenApiParameter(name='subject', type=OpenApiTypes.INT, description='Filter by subject ID'),
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: AssignmentListSerializer(many=True)},
        tags=['Teachers - Assignments']
    ),
    retrieve=extend_schema(
        summary="Get assignment details",
        responses={200: AssignmentSerializer},
        tags=['Teachers - Assignments']
    ),
    create=extend_schema(
        summary="Create assignment",
        request=AssignmentSerializer,
        responses={201: AssignmentSerializer},
        tags=['Teachers - Assignments']
    ),
    update=extend_schema(
        summary="Update assignment",
        request=AssignmentSerializer,
        responses={200: AssignmentSerializer},
        tags=['Teachers - Assignments']
    ),
    partial_update=extend_schema(
        summary="Partially update assignment",
        request=AssignmentSerializer,
        responses={200: AssignmentSerializer},
        tags=['Teachers - Assignments']
    ),
    destroy=extend_schema(
        summary="Delete assignment",
        responses={204: None},
        tags=['Teachers - Assignments']
    ),
)
class AssignmentViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing assignments."""
    queryset = Assignment.objects.all_colleges()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'subject', 'class_obj', 'section', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['assigned_date', 'due_date', 'created_at']
    ordering = ['-assigned_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return AssignmentListSerializer
        return AssignmentSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# ASSIGNMENT SUBMISSION VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List assignment submissions",
        description="Retrieve assignment submissions.",
        parameters=[
            OpenApiParameter(name='assignment', type=OpenApiTypes.INT, description='Filter by assignment ID'),
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter(name='is_late', type=OpenApiTypes.BOOL, description='Filter late submissions'),
        ],
        responses={200: AssignmentSubmissionListSerializer(many=True)},
        tags=['Teachers - Assignment Submissions']
    ),
    retrieve=extend_schema(
        summary="Get assignment submission details",
        responses={200: AssignmentSubmissionSerializer},
        tags=['Teachers - Assignment Submissions']
    ),
    create=extend_schema(
        summary="Submit assignment",
        request=AssignmentSubmissionSerializer,
        responses={201: AssignmentSubmissionSerializer},
        tags=['Teachers - Assignment Submissions']
    ),
    update=extend_schema(
        summary="Update assignment submission",
        request=AssignmentSubmissionSerializer,
        responses={200: AssignmentSubmissionSerializer},
        tags=['Teachers - Assignment Submissions']
    ),
    partial_update=extend_schema(
        summary="Partially update assignment submission",
        request=AssignmentSubmissionSerializer,
        responses={200: AssignmentSubmissionSerializer},
        tags=['Teachers - Assignment Submissions']
    ),
    destroy=extend_schema(
        summary="Delete assignment submission",
        responses={204: None},
        tags=['Teachers - Assignment Submissions']
    ),
)
class AssignmentSubmissionViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing assignment submissions."""
    queryset = AssignmentSubmission.objects.select_related('assignment__class_obj__college', 'student__college')
    related_college_lookup = 'student__college_id'
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assignment', 'student', 'status', 'is_late', 'graded_by']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['submission_date', 'created_at']
    ordering = ['-submission_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return AssignmentSubmissionListSerializer
        return AssignmentSubmissionSerializer


# ============================================================================
# HOMEWORK VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List homework",
        description="Retrieve homework.",
        parameters=[
            OpenApiParameter(name='teacher', type=OpenApiTypes.INT, description='Filter by teacher ID'),
            OpenApiParameter(name='subject', type=OpenApiTypes.INT, description='Filter by subject ID'),
            OpenApiParameter(name='class_obj', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: HomeworkListSerializer(many=True)},
        tags=['Teachers - Homework']
    ),
    retrieve=extend_schema(
        summary="Get homework details",
        responses={200: HomeworkSerializer},
        tags=['Teachers - Homework']
    ),
    create=extend_schema(
        summary="Create homework",
        request=HomeworkSerializer,
        responses={201: HomeworkSerializer},
        tags=['Teachers - Homework']
    ),
    update=extend_schema(
        summary="Update homework",
        request=HomeworkSerializer,
        responses={200: HomeworkSerializer},
        tags=['Teachers - Homework']
    ),
    partial_update=extend_schema(
        summary="Partially update homework",
        request=HomeworkSerializer,
        responses={200: HomeworkSerializer},
        tags=['Teachers - Homework']
    ),
    destroy=extend_schema(
        summary="Delete homework",
        responses={204: None},
        tags=['Teachers - Homework']
    ),
)
class HomeworkViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing homework."""
    queryset = Homework.objects.all_colleges()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'subject', 'class_obj', 'section', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['assigned_date', 'due_date', 'created_at']
    ordering = ['-assigned_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return HomeworkListSerializer
        return HomeworkSerializer

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# HOMEWORK SUBMISSION VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List homework submissions",
        description="Retrieve homework submissions.",
        parameters=[
            OpenApiParameter(name='homework', type=OpenApiTypes.INT, description='Filter by homework ID'),
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='status', type=OpenApiTypes.STR, description='Filter by status'),
        ],
        responses={200: HomeworkSubmissionSerializer(many=True)},
        tags=['Teachers - Homework Submissions']
    ),
    retrieve=extend_schema(
        summary="Get homework submission details",
        responses={200: HomeworkSubmissionSerializer},
        tags=['Teachers - Homework Submissions']
    ),
    create=extend_schema(
        summary="Submit homework",
        request=HomeworkSubmissionSerializer,
        responses={201: HomeworkSubmissionSerializer},
        tags=['Teachers - Homework Submissions']
    ),
    update=extend_schema(
        summary="Update homework submission",
        request=HomeworkSubmissionSerializer,
        responses={200: HomeworkSubmissionSerializer},
        tags=['Teachers - Homework Submissions']
    ),
    partial_update=extend_schema(
        summary="Partially update homework submission",
        request=HomeworkSubmissionSerializer,
        responses={200: HomeworkSubmissionSerializer},
        tags=['Teachers - Homework Submissions']
    ),
    destroy=extend_schema(
        summary="Delete homework submission",
        responses={204: None},
        tags=['Teachers - Homework Submissions']
    ),
)
class HomeworkSubmissionViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing homework submissions."""
    queryset = HomeworkSubmission.objects.select_related('homework__class_obj__college', 'student__college')
    related_college_lookup = 'student__college_id'
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['homework', 'student', 'status', 'checked_by']
    search_fields = ['student__first_name', 'student__last_name']
    ordering_fields = ['completion_date', 'created_at']
    ordering = ['-created_at']
