"""
URL configuration for Reports app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ReportTemplateViewSet,
    GeneratedReportViewSet,
    SavedReportViewSet,
)

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet, basename='reporttemplate')
router.register(r'generated', GeneratedReportViewSet, basename='generatedreport')
router.register(r'saved', SavedReportViewSet, basename='savedreport')

urlpatterns = [
    path('', include(router.urls)),
]
