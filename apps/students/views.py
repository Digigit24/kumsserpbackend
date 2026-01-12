"""
DRF ViewSets for Students app with comprehensive API documentation.
"""
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
)
from apps.core.cache_mixins import CachedReadOnlyMixin
from drf_spectacular.types import OpenApiTypes

from .models import (
    StudentCategory, StudentGroup, Student, Guardian, StudentGuardian,
    StudentAddress, StudentDocument, StudentMedicalRecord, PreviousAcademicRecord,
    StudentPromotion, Certificate, StudentIDCard
)
from .serializers import (
    StudentCategorySerializer,
    StudentGroupSerializer,
    StudentSerializer, StudentListSerializer,
    GuardianSerializer,
    StudentGuardianSerializer,
    StudentAddressSerializer,
    StudentDocumentSerializer,
    StudentMedicalRecordSerializer,
    PreviousAcademicRecordSerializer,
    StudentPromotionSerializer,
    CertificateSerializer,
    StudentIDCardSerializer,
    BulkDeleteSerializer,
)
from apps.core.mixins import CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet


# ============================================================================
# STUDENT CATEGORY VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student categories",
        description="Retrieve student categories for the current college.",
        parameters=[
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: StudentCategorySerializer(many=True)},
        tags=['Students - Categories']
    ),
    retrieve=extend_schema(
        summary="Get student category details",
        responses={200: StudentCategorySerializer},
        tags=['Students - Categories']
    ),
    create=extend_schema(
        summary="Create student category",
        request=StudentCategorySerializer,
        responses={201: StudentCategorySerializer},
        tags=['Students - Categories']
    ),
    update=extend_schema(
        summary="Update student category",
        request=StudentCategorySerializer,
        responses={200: StudentCategorySerializer},
        tags=['Students - Categories']
    ),
    partial_update=extend_schema(
        summary="Partially update student category",
        request=StudentCategorySerializer,
        responses={200: StudentCategorySerializer},
        tags=['Students - Categories']
    ),
    destroy=extend_schema(
        summary="Delete student category",
        responses={204: None},
        tags=['Students - Categories']
    ),
)
class StudentCategoryViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing student categories."""
    queryset = StudentCategory.objects.all_colleges()
    serializer_class = StudentCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# STUDENT GROUP VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student groups",
        description="Retrieve student groups for the current college.",
        parameters=[
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: StudentGroupSerializer(many=True)},
        tags=['Students - Groups']
    ),
    retrieve=extend_schema(
        summary="Get student group details",
        responses={200: StudentGroupSerializer},
        tags=['Students - Groups']
    ),
    create=extend_schema(
        summary="Create student group",
        request=StudentGroupSerializer,
        responses={201: StudentGroupSerializer},
        tags=['Students - Groups']
    ),
    update=extend_schema(
        summary="Update student group",
        request=StudentGroupSerializer,
        responses={200: StudentGroupSerializer},
        tags=['Students - Groups']
    ),
    partial_update=extend_schema(
        summary="Partially update student group",
        request=StudentGroupSerializer,
        responses={200: StudentGroupSerializer},
        tags=['Students - Groups']
    ),
    destroy=extend_schema(
        summary="Delete student group",
        responses={204: None},
        tags=['Students - Groups']
    ),
)
class StudentGroupViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing student groups."""
    queryset = StudentGroup.objects.all_colleges()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# STUDENT VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List students",
        description="Retrieve students for the current college.",
        parameters=[
            OpenApiParameter(name='program', type=OpenApiTypes.INT, description='Filter by program ID'),
            OpenApiParameter(name='current_class', type=OpenApiTypes.INT, description='Filter by class ID'),
            OpenApiParameter(name='current_section', type=OpenApiTypes.INT, description='Filter by section ID'),
            OpenApiParameter(name='category', type=OpenApiTypes.INT, description='Filter by category ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
            OpenApiParameter(name='is_alumni', type=OpenApiTypes.BOOL, description='Filter alumni'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search by name, admission number, email'),
        ],
        responses={200: StudentListSerializer(many=True)},
        tags=['Students']
    ),
    retrieve=extend_schema(
        summary="Get student details",
        responses={200: StudentSerializer},
        tags=['Students']
    ),
    create=extend_schema(
        summary="Create student",
        request=StudentSerializer,
        responses={201: StudentSerializer},
        tags=['Students']
    ),
    update=extend_schema(
        summary="Update student",
        request=StudentSerializer,
        responses={200: StudentSerializer},
        tags=['Students']
    ),
    partial_update=extend_schema(
        summary="Partially update student",
        request=StudentSerializer,
        responses={200: StudentSerializer},
        tags=['Students']
    ),
    destroy=extend_schema(
        summary="Delete student",
        responses={204: None},
        tags=['Students']
    ),
)
class StudentViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    """ViewSet for managing students."""
    queryset = Student.objects.all_colleges()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'current_class', 'current_section', 'category', 'group', 'is_active', 'is_alumni', 'gender']
    search_fields = ['first_name', 'last_name', 'admission_number', 'registration_number', 'email', 'phone']
    ordering_fields = ['admission_number', 'first_name', 'admission_date', 'created_at']
    ordering = ['admission_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer

    def _invalidate_cache(self):
        """Clear cache after mutations - use selective invalidation"""
        try:
            from apps.core.utils import get_current_college_id

            # Clear cache for student-related endpoints only
            view_name = self.__class__.__name__.lower()
            college_id = get_current_college_id()

            patterns = [
                f'views.decorators.cache.cache_page.*.student*',
                f'*student*list*',
                f'*student*retrieve*',
            ]

            if college_id:
                patterns.extend([
                    f'*{college_id}*student*',
                    f'*college_{college_id}*',
                ])

            for pattern in patterns:
                try:
                    keys = cache.keys(pattern)
                    if keys:
                        cache.delete_many(keys)
                except:
                    pass

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Student cache invalidation failed: {e}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        self._invalidate_cache()
        return response

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# GUARDIAN VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List guardians",
        description="Retrieve guardians.",
        parameters=[
            OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Search by name, email, phone'),
        ],
        responses={200: GuardianSerializer(many=True)},
        tags=['Students - Guardians']
    ),
    retrieve=extend_schema(
        summary="Get guardian details",
        responses={200: GuardianSerializer},
        tags=['Students - Guardians']
    ),
    create=extend_schema(
        summary="Create guardian",
        request=GuardianSerializer,
        responses={201: GuardianSerializer},
        tags=['Students - Guardians']
    ),
    update=extend_schema(
        summary="Update guardian",
        request=GuardianSerializer,
        responses={200: GuardianSerializer},
        tags=['Students - Guardians']
    ),
    partial_update=extend_schema(
        summary="Partially update guardian",
        request=GuardianSerializer,
        responses={200: GuardianSerializer},
        tags=['Students - Guardians']
    ),
    destroy=extend_schema(
        summary="Delete guardian",
        responses={204: None},
        tags=['Students - Guardians']
    ),
)
class GuardianViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing guardians."""
    queryset = Guardian.objects.select_related('user')
    related_college_lookup = 'students__student__college_id'
    serializer_class = GuardianSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['relation']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'created_at']
    ordering = ['first_name']


# ============================================================================
# STUDENT GUARDIAN VIEWSET
# ============================================================================


class StudentGuardianFilter(django_filters.FilterSet):
    """Custom filterset for StudentGuardian that handles X-College-ID: all."""
    
    # Use NumberFilter instead of ModelChoiceFilter to bypass FK validation
    # The actual filtering is done by the queryset, validation is the issue
    student = django_filters.NumberFilter(field_name='student_id')
    guardian = django_filters.NumberFilter(field_name='guardian_id')
    
    class Meta:
        model = StudentGuardian
        fields = ['student', 'guardian', 'is_primary', 'is_emergency_contact']


class StudentAddressFilter(django_filters.FilterSet):
    """Custom filterset for StudentAddress."""
    student = django_filters.NumberFilter(field_name='student_id')
    
    class Meta:
        model = StudentAddress
        fields = ['student', 'address_type', 'city', 'state']


class StudentDocumentFilter(django_filters.FilterSet):
    """Custom filterset for StudentDocument."""
    student = django_filters.NumberFilter(field_name='student_id')
    
    class Meta:
        model = StudentDocument
        fields = ['student', 'document_type', 'is_verified', 'is_active']


class StudentMedicalRecordFilter(django_filters.FilterSet):
    """Custom filterset for StudentMedicalRecord."""
    student = django_filters.NumberFilter(field_name='student_id')
    
    class Meta:
        model = StudentMedicalRecord
        fields = ['student', 'is_active']


class PreviousAcademicRecordFilter(django_filters.FilterSet):
    """Custom filterset for PreviousAcademicRecord."""
    student = django_filters.NumberFilter(field_name='student_id')
    
    class Meta:
        model = PreviousAcademicRecord
        fields = ['student', 'level', 'year_of_passing', 'is_active']


class StudentPromotionFilter(django_filters.FilterSet):
    """Custom filterset for StudentPromotion."""
    student = django_filters.NumberFilter(field_name='student_id')
    from_class = django_filters.NumberFilter(field_name='from_class_id')
    to_class = django_filters.NumberFilter(field_name='to_class_id')
    academic_year = django_filters.NumberFilter(field_name='academic_year_id')
    
    class Meta:
        model = StudentPromotion
        fields = ['student', 'from_class', 'to_class', 'academic_year', 'is_active']


class CertificateFilter(django_filters.FilterSet):
    """Custom filterset for Certificate."""
    student = django_filters.NumberFilter(field_name='student_id')
    
    class Meta:
        model = Certificate
        fields = ['student', 'certificate_type', 'is_active']


class StudentIDCardFilter(django_filters.FilterSet):
    """Custom filterset for StudentIDCard."""
    student = django_filters.NumberFilter(field_name='student_id')
    
    class Meta:
        model = StudentIDCard
        fields = ['student', 'is_active', 'is_reissue']


@extend_schema_view(
    list=extend_schema(
        summary="List student-guardian relationships",
        description="Retrieve student-guardian mappings.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='guardian', type=OpenApiTypes.INT, description='Filter by guardian ID'),
            OpenApiParameter(name='is_primary', type=OpenApiTypes.BOOL, description='Filter primary guardians'),
        ],
        responses={200: StudentGuardianSerializer(many=True)},
        tags=['Students - Guardians']
    ),
    retrieve=extend_schema(
        summary="Get student-guardian relationship details",
        responses={200: StudentGuardianSerializer},
        tags=['Students - Guardians']
    ),
    create=extend_schema(
        summary="Link student to guardian",
        request=StudentGuardianSerializer,
        responses={201: StudentGuardianSerializer},
        tags=['Students - Guardians']
    ),
    update=extend_schema(
        summary="Update student-guardian relationship",
        request=StudentGuardianSerializer,
        responses={200: StudentGuardianSerializer},
        tags=['Students - Guardians']
    ),
    partial_update=extend_schema(
        summary="Partially update student-guardian relationship",
        request=StudentGuardianSerializer,
        responses={200: StudentGuardianSerializer},
        tags=['Students - Guardians']
    ),
    destroy=extend_schema(
        summary="Delete student-guardian relationship",
        responses={204: None},
        tags=['Students - Guardians']
    ),
)
class StudentGuardianViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing student-guardian relationships."""
    queryset = StudentGuardian.objects.select_related('student', 'guardian')
    related_college_lookup = 'student__college_id'
    serializer_class = StudentGuardianSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StudentGuardianFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']


# ============================================================================
# STUDENT ADDRESS VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student addresses",
        description="Retrieve student addresses.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='address_type', type=OpenApiTypes.STR, description='Filter by address type'),
        ],
        responses={200: StudentAddressSerializer(many=True)},
        tags=['Students - Addresses']
    ),
    retrieve=extend_schema(
        summary="Get student address details",
        responses={200: StudentAddressSerializer},
        tags=['Students - Addresses']
    ),
    create=extend_schema(
        summary="Create student address",
        request=StudentAddressSerializer,
        responses={201: StudentAddressSerializer},
        tags=['Students - Addresses']
    ),
    update=extend_schema(
        summary="Update student address",
        request=StudentAddressSerializer,
        responses={200: StudentAddressSerializer},
        tags=['Students - Addresses']
    ),
    partial_update=extend_schema(
        summary="Partially update student address",
        request=StudentAddressSerializer,
        responses={200: StudentAddressSerializer},
        tags=['Students - Addresses']
    ),
    destroy=extend_schema(
        summary="Delete student address",
        responses={204: None},
        tags=['Students - Addresses']
    ),
)
class StudentAddressViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing student addresses."""
    queryset = StudentAddress.objects.select_related('student')
    related_college_lookup = 'student__college_id'
    serializer_class = StudentAddressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StudentAddressFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']


# ============================================================================
# STUDENT DOCUMENT VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student documents",
        description="Retrieve student documents.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='document_type', type=OpenApiTypes.STR, description='Filter by document type'),
            OpenApiParameter(name='is_verified', type=OpenApiTypes.BOOL, description='Filter by verification status'),
        ],
        responses={200: StudentDocumentSerializer(many=True)},
        tags=['Students - Documents']
    ),
    retrieve=extend_schema(
        summary="Get student document details",
        responses={200: StudentDocumentSerializer},
        tags=['Students - Documents']
    ),
    create=extend_schema(
        summary="Upload student document",
        request=StudentDocumentSerializer,
        responses={201: StudentDocumentSerializer},
        tags=['Students - Documents']
    ),
    update=extend_schema(
        summary="Update student document",
        request=StudentDocumentSerializer,
        responses={200: StudentDocumentSerializer},
        tags=['Students - Documents']
    ),
    partial_update=extend_schema(
        summary="Partially update student document",
        request=StudentDocumentSerializer,
        responses={200: StudentDocumentSerializer},
        tags=['Students - Documents']
    ),
    destroy=extend_schema(
        summary="Delete student document",
        responses={204: None},
        tags=['Students - Documents']
    ),
)
class StudentDocumentViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing student documents."""
    queryset = StudentDocument.objects.select_related('student')
    related_college_lookup = 'student__college_id'
    serializer_class = StudentDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StudentDocumentFilter
    ordering_fields = ['uploaded_date', 'created_at']
    ordering = ['-uploaded_date']

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# STUDENT MEDICAL RECORD VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student medical records",
        description="Retrieve student medical records.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
        ],
        responses={200: StudentMedicalRecordSerializer(many=True)},
        tags=['Students - Medical Records']
    ),
    retrieve=extend_schema(
        summary="Get student medical record details",
        responses={200: StudentMedicalRecordSerializer},
        tags=['Students - Medical Records']
    ),
    create=extend_schema(
        summary="Create student medical record",
        request=StudentMedicalRecordSerializer,
        responses={201: StudentMedicalRecordSerializer},
        tags=['Students - Medical Records']
    ),
    update=extend_schema(
        summary="Update student medical record",
        request=StudentMedicalRecordSerializer,
        responses={200: StudentMedicalRecordSerializer},
        tags=['Students - Medical Records']
    ),
    partial_update=extend_schema(
        summary="Partially update student medical record",
        request=StudentMedicalRecordSerializer,
        responses={200: StudentMedicalRecordSerializer},
        tags=['Students - Medical Records']
    ),
    destroy=extend_schema(
        summary="Delete student medical record",
        responses={204: None},
        tags=['Students - Medical Records']
    ),
)
class StudentMedicalRecordViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing student medical records."""
    queryset = StudentMedicalRecord.objects.select_related('student')
    related_college_lookup = 'student__college_id'
    serializer_class = StudentMedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StudentMedicalRecordFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# PREVIOUS ACADEMIC RECORD VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List previous academic records",
        description="Retrieve student previous academic records.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='level', type=OpenApiTypes.STR, description='Filter by education level'),
        ],
        responses={200: PreviousAcademicRecordSerializer(many=True)},
        tags=['Students - Academic Records']
    ),
    retrieve=extend_schema(
        summary="Get previous academic record details",
        responses={200: PreviousAcademicRecordSerializer},
        tags=['Students - Academic Records']
    ),
    create=extend_schema(
        summary="Create previous academic record",
        request=PreviousAcademicRecordSerializer,
        responses={201: PreviousAcademicRecordSerializer},
        tags=['Students - Academic Records']
    ),
    update=extend_schema(
        summary="Update previous academic record",
        request=PreviousAcademicRecordSerializer,
        responses={200: PreviousAcademicRecordSerializer},
        tags=['Students - Academic Records']
    ),
    partial_update=extend_schema(
        summary="Partially update previous academic record",
        request=PreviousAcademicRecordSerializer,
        responses={200: PreviousAcademicRecordSerializer},
        tags=['Students - Academic Records']
    ),
    destroy=extend_schema(
        summary="Delete previous academic record",
        responses={204: None},
        tags=['Students - Academic Records']
    ),
)
class PreviousAcademicRecordViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing previous academic records."""
    queryset = PreviousAcademicRecord.objects.all()
    serializer_class = PreviousAcademicRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PreviousAcademicRecordFilter
    ordering_fields = ['year_of_passing', 'created_at']
    ordering = ['-year_of_passing']

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# STUDENT PROMOTION VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student promotions",
        description="Retrieve student promotion records.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='academic_year', type=OpenApiTypes.INT, description='Filter by academic year ID'),
        ],
        responses={200: StudentPromotionSerializer(many=True)},
        tags=['Students - Promotions']
    ),
    retrieve=extend_schema(
        summary="Get student promotion details",
        responses={200: StudentPromotionSerializer},
        tags=['Students - Promotions']
    ),
    create=extend_schema(
        summary="Create student promotion",
        request=StudentPromotionSerializer,
        responses={201: StudentPromotionSerializer},
        tags=['Students - Promotions']
    ),
    update=extend_schema(
        summary="Update student promotion",
        request=StudentPromotionSerializer,
        responses={200: StudentPromotionSerializer},
        tags=['Students - Promotions']
    ),
    partial_update=extend_schema(
        summary="Partially update student promotion",
        request=StudentPromotionSerializer,
        responses={200: StudentPromotionSerializer},
        tags=['Students - Promotions']
    ),
    destroy=extend_schema(
        summary="Delete student promotion",
        responses={204: None},
        tags=['Students - Promotions']
    ),
)
class StudentPromotionViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing student promotions."""
    queryset = StudentPromotion.objects.select_related('student', 'from_class', 'to_class', 'academic_year')
    related_college_lookup = 'student__college_id'
    serializer_class = StudentPromotionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StudentPromotionFilter
    ordering_fields = ['promotion_date', 'created_at']
    ordering = ['-promotion_date']

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# CERTIFICATE VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List certificates",
        description="Retrieve student certificates.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='certificate_type', type=OpenApiTypes.STR, description='Filter by certificate type'),
        ],
        responses={200: CertificateSerializer(many=True)},
        tags=['Students - Certificates']
    ),
    retrieve=extend_schema(
        summary="Get certificate details",
        responses={200: CertificateSerializer},
        tags=['Students - Certificates']
    ),
    create=extend_schema(
        summary="Issue certificate",
        request=CertificateSerializer,
        responses={201: CertificateSerializer},
        tags=['Students - Certificates']
    ),
    update=extend_schema(
        summary="Update certificate",
        request=CertificateSerializer,
        responses={200: CertificateSerializer},
        tags=['Students - Certificates']
    ),
    partial_update=extend_schema(
        summary="Partially update certificate",
        request=CertificateSerializer,
        responses={200: CertificateSerializer},
        tags=['Students - Certificates']
    ),
    destroy=extend_schema(
        summary="Delete certificate",
        responses={204: None},
        tags=['Students - Certificates']
    ),
)
class CertificateViewSet(RelatedCollegeScopedModelViewSet):
    """ViewSet for managing certificates."""
    queryset = Certificate.objects.select_related('student')
    related_college_lookup = 'student__college_id'
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CertificateFilter
    search_fields = ['certificate_number', 'student__first_name', 'student__last_name']
    ordering_fields = ['issue_date', 'created_at']
    ordering = ['-issue_date']

    def perform_destroy(self, instance):
        instance.soft_delete()


# ============================================================================
# STUDENT ID CARD VIEWSET
# ============================================================================


@extend_schema_view(
    list=extend_schema(
        summary="List student ID cards",
        description="Retrieve student ID cards.",
        parameters=[
            OpenApiParameter(name='student', type=OpenApiTypes.INT, description='Filter by student ID'),
            OpenApiParameter(name='is_active', type=OpenApiTypes.BOOL, description='Filter by active status'),
        ],
        responses={200: StudentIDCardSerializer(many=True)},
        tags=['Students - ID Cards']
    ),
    retrieve=extend_schema(
        summary="Get student ID card details",
        responses={200: StudentIDCardSerializer},
        tags=['Students - ID Cards']
    ),
    create=extend_schema(
        summary="Issue student ID card",
        request=StudentIDCardSerializer,
        responses={201: StudentIDCardSerializer},
        tags=['Students - ID Cards']
    ),
    update=extend_schema(
        summary="Update student ID card",
        request=StudentIDCardSerializer,
        responses={200: StudentIDCardSerializer},
        tags=['Students - ID Cards']
    ),
    partial_update=extend_schema(
        summary="Partially update student ID card",
        request=StudentIDCardSerializer,
        responses={200: StudentIDCardSerializer},
        tags=['Students - ID Cards']
    ),
    destroy=extend_schema(
        summary="Delete student ID card",
        responses={204: None},
        tags=['Students - ID Cards']
    ),
)
class StudentIDCardViewSet(CollegeScopedModelViewSet):
    """ViewSet for managing student ID cards."""
    queryset = StudentIDCard.objects.all()
    serializer_class = StudentIDCardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StudentIDCardFilter
    search_fields = ['card_number', 'student__first_name', 'student__last_name']
    ordering_fields = ['issue_date', 'created_at']
    ordering = ['-issue_date']

    def perform_destroy(self, instance):
        instance.soft_delete()
