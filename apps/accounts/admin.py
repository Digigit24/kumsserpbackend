"""
Django admin configuration for accounts app models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User, Role, UserRole, Department, UserProfile


class CollegeAwareAdmin(admin.ModelAdmin):
    """
    Admin base that bypasses college scoping to allow global visibility.
    """

    def get_queryset(self, request):
        manager = getattr(self.model, 'objects', None)
        if manager and hasattr(manager, 'all_colleges'):
            return manager.all_colleges()
        return super().get_queryset(request)


class AuditFieldsAdmin(CollegeAwareAdmin):
    """
    Base admin that exposes audit fields and auto-fills created/updated by.
    """
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'created_by') and not change:
            obj.created_by = request.user
        if hasattr(obj, 'updated_by'):
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users with the custom User model."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'middle_name',
            'college', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'is_verified',
        )


class CustomUserChangeForm(UserChangeForm):
    """Custom form for updating users with the custom User model."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password',
            'first_name', 'last_name', 'middle_name',
            'phone', 'gender', 'date_of_birth', 'avatar',
            'college', 'user_type',
            'is_active', 'is_staff', 'is_superuser', 'is_verified',
            'groups', 'user_permissions',
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for the custom User model."""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'college', 'user_type', 'is_staff', 'is_superuser',
        'is_active', 'is_verified', 'date_joined',
    ]
    list_filter = [
        'user_type', 'is_staff', 'is_superuser',
        'is_active', 'is_verified', 'college',
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    filter_horizontal = ['groups', 'user_permissions']
    readonly_fields = ['date_joined', 'last_login', 'last_password_change', 'failed_login_attempts', 'lockout_until']
    list_select_related = ['college']

    fieldsets = (
        ('Credentials', {'fields': ('username', 'email', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'middle_name', 'last_name',
                'phone', 'gender', 'date_of_birth', 'avatar',
            )
        }),
        ('College & Role', {'fields': ('college', 'user_type')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_verified', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            )
        }),
        ('Security', {
            'fields': (
                'last_login_ip', 'failed_login_attempts',
                'lockout_until', 'last_password_change',
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name', 'middle_name',
                'college', 'user_type',
                'password1', 'password2',
                'is_active', 'is_verified', 'is_staff', 'is_superuser',
            ),
        }),
    )


@admin.register(Role)
class RoleAdmin(AuditFieldsAdmin):
    """Admin interface for Role model."""
    list_display = ['name', 'code', 'college', 'display_order', 'is_active']
    list_filter = ['college', 'is_active']
    search_fields = ['name', 'code', 'description', 'college__name']
    ordering = ['display_order', 'name']
    fieldsets = (
        ('Role Information', {
            'fields': ('college', 'name', 'code', 'description', 'permissions')
        }),
        ('Display & Status', {
            'fields': ('display_order', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserRole)
class UserRoleAdmin(AuditFieldsAdmin):
    """Admin interface for UserRole assignments."""
    list_display = [
        'user', 'role', 'college', 'assigned_by',
        'assigned_at', 'expires_at', 'is_active'
    ]
    list_filter = ['college', 'role', 'is_active']
    search_fields = [
        'user__username', 'user__email',
        'role__name', 'assigned_by__username'
    ]
    autocomplete_fields = ['user', 'role', 'assigned_by', 'college']
    readonly_fields = AuditFieldsAdmin.readonly_fields + ['assigned_at']
    ordering = ['-assigned_at']
    fieldsets = (
        ('Assignment Details', {
            'fields': ('college', 'user', 'role', 'assigned_by', 'assigned_at', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(AuditFieldsAdmin):
    """Admin interface for Department model."""
    list_display = ['name', 'code', 'college', 'hod', 'display_order', 'is_active']
    list_filter = ['college', 'is_active']
    search_fields = ['name', 'code', 'short_name', 'college__name', 'hod__username']
    autocomplete_fields = ['college', 'hod']
    ordering = ['display_order', 'name']
    fieldsets = (
        ('Department Information', {
            'fields': ('college', 'code', 'name', 'short_name', 'description', 'hod')
        }),
        ('Display & Status', {
            'fields': ('display_order', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(AuditFieldsAdmin):
    """Admin interface for UserProfile model."""
    list_display = ['user', 'college', 'department', 'city', 'state', 'is_active']
    list_filter = ['college', 'department', 'is_active']
    search_fields = [
        'user__username', 'user__email',
        'city', 'state', 'country',
        'emergency_contact_name', 'emergency_contact_phone'
    ]
    autocomplete_fields = ['college', 'user', 'department']
    ordering = ['user__username']
    fieldsets = (
        ('Profile Ownership', {
            'fields': ('college', 'user', 'department')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode', 'country')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')
        }),
        ('Personal Details', {
            'fields': ('blood_group', 'nationality', 'religion', 'caste', 'profile_data')
        }),
        ('Online Presence', {
            'fields': ('linkedin_url', 'website_url', 'bio')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
