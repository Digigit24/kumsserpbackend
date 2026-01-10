"""
Django admin configuration for core app models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    College,
    AcademicYear,
    AcademicSession,
    Holiday,
    Weekend,
    SystemSetting,
    NotificationSetting,
    ActivityLog,
    OrganizationNode,
    DynamicRole,
    HierarchyPermission,
    RolePermission,
    UserRole,
    Team,
    HierarchyTeamMember
)
from mptt.admin import MPTTModelAdmin


class CollegeAwareAdmin(admin.ModelAdmin):
    """
    Admin base that bypasses college scoping to allow global visibility.
    """

    def get_queryset(self, request):
        manager = getattr(self.model, 'objects', None)
        if manager and hasattr(manager, 'all_colleges'):
            return manager.all_colleges()
        return super().get_queryset(request)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Override to show all FK options regardless of college context."""
        if db_field.remote_field and hasattr(db_field.remote_field.model.objects, 'all_colleges'):
            kwargs['queryset'] = db_field.remote_field.model.objects.all_colleges()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(College)
class CollegeAdmin(CollegeAwareAdmin):
    """Admin interface for College model."""
    list_display = [
        'code', 'name', 'short_name', 'city', 'state',
        'is_main', 'is_active', 'display_order'
    ]
    list_filter = ['is_active', 'is_main', 'state', 'country']
    search_fields = ['code', 'name', 'short_name', 'email', 'phone', 'city']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'short_name')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode', 'country')
        }),
        ('Additional Details', {
            'fields': ('logo', 'established_date', 'affiliation_number')
        }),
        ('Branding', {
            'fields': ('primary_color', 'secondary_color')
        }),
        ('Configuration', {
            'fields': ('settings', 'is_main', 'display_order', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['display_order', 'name']


@admin.register(AcademicYear)
class AcademicYearAdmin(CollegeAwareAdmin):
    """Admin interface for AcademicYear model."""
    list_display = ['year', 'college', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['is_current', 'is_active', 'start_date']
    search_fields = ['year', 'college__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Academic Year Information', {
            'fields': ('college', 'year', 'start_date', 'end_date', 'is_current', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-start_date']

    def save_model(self, request, obj, form, change):
        """Automatically populate audit fields."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AcademicSession)
class AcademicSessionAdmin(CollegeAwareAdmin):
    """Admin interface for AcademicSession model."""
    list_display = [
        'name', 'college', 'academic_year', 'semester',
        'start_date', 'end_date', 'is_current', 'is_active'
    ]
    list_filter = ['is_current', 'is_active', 'semester', 'college', 'academic_year']
    search_fields = ['name', 'college__name', 'academic_year__year']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Session Information', {
            'fields': ('college', 'academic_year', 'name', 'semester')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date', 'is_current', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-start_date']

    def save_model(self, request, obj, form, change):
        """Automatically populate audit fields."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Holiday)
class HolidayAdmin(CollegeAwareAdmin):
    """Admin interface for Holiday model."""
    list_display = ['name', 'date', 'holiday_type', 'college', 'is_active']
    list_filter = ['holiday_type', 'is_active', 'date', 'college']
    search_fields = ['name', 'college__name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    date_hierarchy = 'date'
    fieldsets = (
        ('Holiday Information', {
            'fields': ('college', 'name', 'date', 'holiday_type', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['date']

    def save_model(self, request, obj, form, change):
        """Automatically populate audit fields."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Weekend)
class WeekendAdmin(CollegeAwareAdmin):
    """Admin interface for Weekend model."""
    list_display = ['college', 'get_day_name', 'is_active']
    list_filter = ['day', 'is_active', 'college']
    search_fields = ['college__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('Weekend Configuration', {
            'fields': ('college', 'day', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['college', 'day']

    def get_day_name(self, obj):
        """Display the day name instead of number."""
        return obj.get_day_display()
    get_day_name.short_description = 'Day'

    def save_model(self, request, obj, form, change):
        """Automatically populate audit fields."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SystemSetting)
class SystemSettingAdmin(CollegeAwareAdmin):
    """Admin interface for SystemSetting model."""
    list_display = ['college', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['college__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('System Settings', {
            'fields': ('college', 'settings', 'is_active'),
            'description': 'JSON structure should include: system, email, sms, security, features'
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically populate audit fields."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(NotificationSetting)
class NotificationSettingAdmin(CollegeAwareAdmin):
    """Admin interface for NotificationSetting model."""
    list_display = [
        'college', 'sms_enabled', 'email_enabled', 'whatsapp_enabled',
        'attendance_notif', 'fee_reminder', 'is_active'
    ]
    list_filter = [
        'sms_enabled', 'email_enabled', 'whatsapp_enabled',
        'attendance_notif', 'fee_reminder', 'is_active', 'college'
    ]
    search_fields = ['college__name', 'sms_gateway', 'email_gateway']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    fieldsets = (
        ('College', {
            'fields': ('college',)
        }),
        ('SMS Configuration', {
            'fields': ('sms_enabled', 'sms_gateway', 'sms_api_key', 'sms_sender_id')
        }),
        ('Email Configuration', {
            'fields': ('email_enabled', 'email_gateway', 'email_api_key', 'email_from')
        }),
        ('WhatsApp Configuration', {
            'fields': ('whatsapp_enabled', 'whatsapp_api_key', 'whatsapp_number')
        }),
        ('Notification Preferences', {
            'fields': ('attendance_notif', 'fee_reminder', 'fee_days')
        }),
        ('Advanced Configuration', {
            'fields': ('notif_settings', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically populate audit fields."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ActivityLog)
class ActivityLogAdmin(CollegeAwareAdmin):
    """Admin interface for ActivityLog model."""
    list_display = [
        'timestamp', 'action', 'user', 'model_name',
        'college', 'ip_address_display'
    ]
    list_filter = ['action', 'timestamp', 'college', 'model_name']
    search_fields = [
        'user__username', 'model_name', 'object_id',
        'description', 'ip_address'
    ]
    readonly_fields = [
        'user', 'college', 'action', 'model_name', 'object_id',
        'description', 'metadata', 'ip_address', 'user_agent', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        """Disable manual addition of activity logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make activity logs read-only."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deletion of activity logs."""
        return False

    def ip_address_display(self, obj):
        """Display IP address with color coding."""
        if obj.ip_address:
            return format_html(
                '<span style="color: #0066cc;">{}</span>',
                obj.ip_address
            )
        return '-'
    ip_address_display.short_description = 'IP Address'


# ============================================================================
# ORGANIZATIONAL HIERARCHY ADMIN
# ============================================================================

@admin.register(OrganizationNode)
class OrganizationNodeAdmin(MPTTModelAdmin):
    """Admin for Organization Node with tree structure."""
    list_display = ['name', 'node_type', 'role', 'user', 'college', 'is_active', 'order']
    list_filter = ['node_type', 'is_active', 'college']
    search_fields = ['name', 'description']
    autocomplete_fields = ['user', 'college', 'role', 'parent']
    mptt_level_indent = 20


@admin.register(DynamicRole)
class DynamicRoleAdmin(admin.ModelAdmin):
    """Admin for Dynamic Roles."""
    list_display = ['name', 'code', 'level', 'is_global', 'college', 'is_active']
    list_filter = ['is_global', 'is_active', 'college']
    search_fields = ['name', 'code', 'description']
    prepopulated_fields = {'code': ('name',)}


@admin.register(HierarchyPermission)
class HierarchyPermissionAdmin(admin.ModelAdmin):
    """Admin for Hierarchy Permissions."""
    list_display = ['code', 'name', 'app_label', 'resource', 'action', 'category']
    list_filter = ['app_label', 'action', 'category']
    search_fields = ['code', 'name', 'description']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """Admin for Role Permission mappings."""
    list_display = ['role', 'permission', 'scope', 'can_delegate']
    list_filter = ['scope', 'can_delegate', 'role']
    search_fields = ['role__name', 'permission__code']
    autocomplete_fields = ['role', 'permission']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin for User Role assignments."""
    list_display = ['user', 'role', 'college', 'assigned_by', 'assigned_at', 'is_active']
    list_filter = ['is_active', 'college', 'role']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'role__name']
    autocomplete_fields = ['user', 'role', 'college', 'assigned_by']
    raw_id_fields = ['department']
    date_hierarchy = 'assigned_at'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin for Teams."""
    list_display = ['name', 'team_type', 'lead_user', 'college', 'is_active']
    list_filter = ['team_type', 'is_active', 'college']
    search_fields = ['name', 'description']
    autocomplete_fields = ['node', 'lead_user', 'college']


@admin.register(HierarchyTeamMember)
class HierarchyTeamMemberAdmin(admin.ModelAdmin):
    """Admin for Team Members."""
    list_display = ['user', 'team', 'role_in_team', 'auto_assigned', 'joined_at']
    list_filter = ['role_in_team', 'auto_assigned', 'team__team_type']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'team__name']
    autocomplete_fields = ['team', 'user']
    date_hierarchy = 'joined_at'
