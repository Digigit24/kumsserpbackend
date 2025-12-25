from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedMixin, CollegeScopedModelViewSet
from .models import ReportTemplate, GeneratedReport, SavedReport
from .serializers import (
    ReportTemplateSerializer,
    GeneratedReportSerializer,
    SavedReportSerializer,
)


class RelatedCollegeScopedModelViewSet(CollegeScopedMixin, viewsets.ModelViewSet):
    """
    Scopes by college via a related lookup path when model lacks direct college FK.
    """
    related_college_lookup = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

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


class ReportTemplateViewSet(CollegeScopedModelViewSet):
    queryset = ReportTemplate.objects.all_colleges()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class GeneratedReportViewSet(RelatedCollegeScopedModelViewSet):
    queryset = GeneratedReport.objects.select_related('template', 'generated_by')
    serializer_class = GeneratedReportSerializer
    related_college_lookup = 'template__college_id'
    filterset_fields = ['template', 'generated_by', 'generation_date', 'is_active']
    ordering_fields = ['generation_date', 'created_at']
    ordering = ['-generation_date']


class SavedReportViewSet(CollegeScopedModelViewSet):
    queryset = SavedReport.objects.select_related('college', 'user').all_colleges()
    serializer_class = SavedReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report_type', 'user', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
