from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import (
    CollegeScopedMixin, CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet
)
from .models import ReportTemplate, GeneratedReport, SavedReport
from .serializers import (
    ReportTemplateSerializer,
    GeneratedReportSerializer,
    SavedReportSerializer,
)


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
    queryset = SavedReport.objects.all_colleges().select_related('college', 'user')
    serializer_class = SavedReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report_type', 'user', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
