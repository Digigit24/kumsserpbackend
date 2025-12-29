"""
DRF Serializers for Core app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    College,
    AcademicYear,
    AcademicSession,
    Holiday,
    Weekend,
    SystemSetting,
    NotificationSetting,
    ActivityLog,
    Permission,
    TeamMembership
)

User = get_user_model()


# ============================================================================
# BASE SERIALIZERS
# ============================================================================


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for nested representations."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class TenantAuditMixin(serializers.Serializer):
    """Mixin to include audit fields in serializers."""
    created_by = UserBasicSerializer(read_only=True)
    updated_by = UserBasicSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# ============================================================================
# COLLEGE SERIALIZERS
# ============================================================================


class CollegeListSerializer(serializers.ModelSerializer):
    """Serializer for listing colleges (minimal fields)."""

    class Meta:
        model = College
        fields = [
            'id', 'code', 'name', 'short_name', 'city',
            'state', 'country', 'is_main', 'is_active'
        ]
        read_only_fields = ['id']


class CollegeSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for College model with all fields."""

    class Meta:
        model = College
        fields = [
            'id', 'code', 'name', 'short_name',
            'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'pincode', 'country',
            'logo', 'established_date', 'affiliation_number',
            'primary_color', 'secondary_color',
            'settings', 'is_main', 'display_order', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def validate_code(self, value):
        """Ensure college code is unique."""
        instance = self.instance
        if College.objects.filter(code=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("College with this code already exists.")
        return value.upper()

    def validate_settings(self, value):
        """Validate college settings JSON structure."""
        if value:
            required_keys = ['academic', 'fees', 'notifications', 'theme']
            if not all(key in value for key in required_keys):
                raise serializers.ValidationError(
                    f"Settings must contain all required keys: {', '.join(required_keys)}"
                )
        return value


class CollegeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating colleges (excludes audit fields)."""

    class Meta:
        model = College
        fields = [
            'code', 'name', 'short_name',
            'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'state', 'pincode', 'country',
            'logo', 'established_date', 'affiliation_number',
            'primary_color', 'secondary_color',
            'settings', 'is_main', 'display_order', 'is_active'
        ]

    def validate_code(self, value):
        """Ensure college code is unique."""
        if College.objects.filter(code=value).exists():
            raise serializers.ValidationError("College with this code already exists.")
        return value.upper()


# ============================================================================
# ACADEMIC YEAR SERIALIZERS
# ============================================================================


class AcademicYearSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for AcademicYear model."""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = AcademicYear
        fields = [
            'id', 'college', 'college_name',
            'year', 'start_date', 'end_date',
            'is_current', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Validate that end_date is after start_date."""
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] <= attrs['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        return attrs


# ============================================================================
# ACADEMIC SESSION SERIALIZERS
# ============================================================================


class AcademicSessionSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for AcademicSession model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    academic_year_label = serializers.CharField(source='academic_year.year', read_only=True)

    class Meta:
        model = AcademicSession
        fields = [
            'id', 'college', 'college_name',
            'academic_year', 'academic_year_label',
            'name', 'semester', 'start_date', 'end_date',
            'is_current', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'academic_year_label',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]

    def validate_semester(self, value):
        """Validate semester is between 1 and 8."""
        if not 1 <= value <= 8:
            raise serializers.ValidationError("Semester must be between 1 and 8.")
        return value

    def validate(self, attrs):
        """Validate that end_date is after start_date."""
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] <= attrs['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        return attrs


# ============================================================================
# HOLIDAY SERIALIZERS
# ============================================================================


class HolidaySerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for Holiday model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    holiday_type_display = serializers.CharField(source='get_holiday_type_display', read_only=True)

    class Meta:
        model = Holiday
        fields = [
            'id', 'college', 'college_name',
            'name', 'date', 'holiday_type', 'holiday_type_display',
            'description', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'holiday_type_display',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# WEEKEND SERIALIZERS
# ============================================================================


class WeekendSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for Weekend model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    day_display = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = Weekend
        fields = [
            'id', 'college', 'college_name',
            'day', 'day_display', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'day_display',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# SYSTEM SETTING SERIALIZERS
# ============================================================================


class SystemSettingSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for SystemSetting model."""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = SystemSetting
        fields = [
            'id', 'college', 'college_name', 'settings', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def validate_settings(self, value):
        """Validate system settings JSON structure."""
        if value:
            required_keys = ['system', 'email', 'sms', 'security', 'features']
            if not all(key in value for key in required_keys):
                raise serializers.ValidationError(
                    f"Settings must contain all required keys: {', '.join(required_keys)}"
                )
        return value


# ============================================================================
# NOTIFICATION SETTING SERIALIZERS
# ============================================================================


class NotificationSettingSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for NotificationSetting model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = NotificationSetting
        fields = [
            'id', 'college', 'college_name',
            'sms_enabled', 'sms_gateway', 'sms_api_key', 'sms_sender_id',
            'email_enabled', 'email_gateway', 'email_api_key', 'email_from',
            'whatsapp_enabled', 'whatsapp_api_key', 'whatsapp_number',
            'attendance_notif', 'fee_reminder', 'fee_days',
            'notif_settings', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'sms_api_key': {'write_only': True},
            'email_api_key': {'write_only': True},
            'whatsapp_api_key': {'write_only': True},
        }


# ============================================================================
# ACTIVITY LOG SERIALIZERS
# ============================================================================


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model (read-only)."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_name',
            'college', 'college_name',
            'action', 'action_display', 'model_name', 'object_id',
            'description', 'metadata',
            'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = fields  # All fields are read-only


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================


class BulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk delete operations."""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of IDs to delete"
    )


class BulkActivateSerializer(serializers.Serializer):
    """Serializer for bulk activate/deactivate operations."""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of IDs to activate/deactivate"
    )
    is_active = serializers.BooleanField(help_text="Set active status")


# ============================================================================
# PERMISSION SYSTEM SERIALIZERS
# ============================================================================


class PermissionSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for Permission model."""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Permission
        fields = [
            'id', 'college', 'college_name', 'role', 'permissions_json',
            'created_at', 'updated_at', 'created_by', 'updated_by', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate_permissions_json(self, value):
        """
        Validate that permissions_json structure is valid.
        """
        from apps.core.permissions.registry import PERMISSION_REGISTRY, AVAILABLE_SCOPES

        for resource, actions in value.items():
            if resource not in PERMISSION_REGISTRY:
                raise serializers.ValidationError(f"Invalid resource: {resource}")

            for action, config in actions.items():
                if action not in PERMISSION_REGISTRY[resource]['actions']:
                    raise serializers.ValidationError(
                        f"Invalid action '{action}' for resource '{resource}'"
                    )

                if 'enabled' not in config or 'scope' not in config:
                    raise serializers.ValidationError(
                        f"Missing 'enabled' or 'scope' in {resource}.{action}"
                    )

                if config['scope'] not in AVAILABLE_SCOPES:
                    raise serializers.ValidationError(f"Invalid scope: {config['scope']}")

        return value


class TeamMembershipSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for TeamMembership model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    leader_name = serializers.CharField(source='leader.get_full_name', read_only=True)
    member_name = serializers.CharField(source='member.get_full_name', read_only=True)

    class Meta:
        model = TeamMembership
        fields = [
            'id', 'college', 'college_name',
            'leader', 'leader_name',
            'member', 'member_name',
            'relationship_type', 'resource',
            'created_at', 'updated_at', 'created_by', 'updated_by', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
