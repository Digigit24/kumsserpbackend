from django.contrib import admin

from .models import ReportTemplate, GeneratedReport, SavedReport


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'report_type', 'is_active')
    search_fields = ('name', 'report_type')
    list_filter = ('college', 'report_type', 'is_active')


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('template', 'generated_by', 'generation_date', 'is_active')
    list_filter = ('generation_date', 'is_active')


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'college', 'report_type', 'is_active')
    search_fields = ('name', 'report_type')
    list_filter = ('college', 'report_type', 'is_active')
