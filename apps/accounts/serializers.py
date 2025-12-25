"""
DRF Serializers for Accounts app models.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from dj_rest_auth.serializers import TokenSerializer as DRATokenSerializer

from .models import (
    User,
    Role,
    UserRole,
    Department,
    UserProfile,
    UserType,
    GenderChoices
)
from apps.core.models import College


# ============================================================================
# BASE SERIALIZERS
# ============================================================================


class CollegeBasicSerializer(serializers.ModelSerializer):
    """Basic college information for nested representations."""

    class Meta:
        model = College
        fields = ['id', 'code', 'name', 'short_name']
        read_only_fields = fields


class TenantAuditMixin(serializers.Serializer):
    """Mixin to include audit fields in serializers."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# ============================================================================
# USER SERIALIZERS
# ============================================================================


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for listing users (minimal fields)."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name',
            'user_type', 'user_type_display',
            'college', 'college_name',
            'is_active', 'is_verified', 'date_joined'
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    """Full serializer for User model with all fields."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'first_name', 'last_name', 'middle_name', 'full_name',
            'gender', 'gender_display', 'date_of_birth', 'avatar',
            'college', 'college_name',
            'user_type', 'user_type_display',
            'is_active', 'is_staff', 'is_verified',
            'last_login', 'last_login_ip',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'college_name', 'user_type_display', 'gender_display',
            'last_login', 'last_login_ip', 'date_joined',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        """Ensure username is unique."""
        instance = self.instance
        if User.objects.filter(username=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Username already exists.")
        return value.lower()

    def validate_email(self, value):
        """Ensure email is unique."""
        instance = self.instance
        if User.objects.filter(email=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value.lower()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'password', 'password_confirm',
            'first_name', 'last_name', 'middle_name',
            'gender', 'date_of_birth', 'avatar',
            'college', 'user_type', 'is_active'
        ]

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs

    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = [
            'email', 'phone',
            'first_name', 'last_name', 'middle_name',
            'gender', 'date_of_birth', 'avatar'
        ]

    def validate_email(self, value):
        """Ensure email is unique."""
        instance = self.instance
        if User.objects.filter(email=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value.lower()


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs

    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class TokenWithUserSerializer(serializers.Serializer):
    """
    Enhanced token serializer that returns comprehensive user details,
    primary college ID, and all accessible college IDs for multi-tenancy support.
    Includes user roles, permissions, and complete profile information.
    """
    key = serializers.CharField(source='key')
    message = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    college_id = serializers.SerializerMethodField()
    tenant_ids = serializers.SerializerMethodField()
    accessible_colleges = serializers.SerializerMethodField()
    user_roles = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    def get_user(self, obj):
        """Return full user details."""
        user = getattr(obj, 'user', None)
        if user:
            return UserSerializer(user).data
        return None

    def get_message(self, obj):
        """Return a success message."""
        user = getattr(obj, 'user', None)
        if user:
            return f"Welcome back, {user.get_full_name()}! Login successful."
        return "Login successful"

    def get_college_id(self, obj):
        """Return the user's primary college ID."""
        user = getattr(obj, 'user', None)
        if not user:
            return None
        if not getattr(user, 'college_id', None) and (user.is_superuser or user.is_staff):
            # Superusers/staff without a college get sentinel 0 for frontend handling
            return 0
        return user.college_id

    def get_tenant_ids(self, obj):
        """
        Return list of all college IDs the user has access to.
        - For superusers/staff: returns [0] to indicate access to all colleges
        - For regular users: returns their primary college + colleges where they have roles
        """
        user = getattr(obj, 'user', None)
        if not user:
            return []

        # Superusers and staff have access to all colleges
        if user.is_superuser or user.is_staff:
            if not user.college_id:
                return [0]  # Sentinel value for "all colleges"

        # Get user's primary college
        tenant_ids = []
        if user.college_id:
            tenant_ids.append(user.college_id)

        # Get colleges where user has active roles (using all_colleges to bypass scoping)
        from .models import UserRole
        role_college_ids = UserRole.objects.all_colleges().filter(
            user=user,
            is_active=True
        ).values_list('college_id', flat=True).distinct()

        # Add role college IDs that aren't already in the list
        for college_id in role_college_ids:
            if college_id and college_id not in tenant_ids:
                tenant_ids.append(college_id)

        return tenant_ids if tenant_ids else [0] if (user.is_superuser or user.is_staff) else []

    def get_accessible_colleges(self, obj):
        """
        Return detailed information about all colleges the user can access.
        """
        user = getattr(obj, 'user', None)
        if not user:
            return []

        tenant_ids = self.get_tenant_ids(obj)

        # If user has sentinel value 0 (superuser with no college), return all colleges
        if 0 in tenant_ids and not user.college_id:
            colleges = College.objects.all_colleges().filter(is_active=True)
            return CollegeBasicSerializer(colleges, many=True).data

        # Return specific colleges user has access to
        colleges = College.objects.all_colleges().filter(
            id__in=[tid for tid in tenant_ids if tid != 0],
            is_active=True
        )
        return CollegeBasicSerializer(colleges, many=True).data

    def get_user_roles(self, obj):
        """
        Return all active roles assigned to the user.
        """
        user = getattr(obj, 'user', None)
        if not user:
            return []

        # Get all active roles for the user (using all_colleges to bypass scoping)
        user_roles = UserRole.objects.all_colleges().filter(
            user=user,
            is_active=True
        ).select_related('role', 'college')

        roles_data = []
        for user_role in user_roles:
            roles_data.append({
                'id': user_role.id,
                'role_id': user_role.role.id,
                'role_name': user_role.role.name,
                'role_code': user_role.role.code,
                'college_id': user_role.college_id,
                'college_name': user_role.college.short_name if user_role.college else None,
                'assigned_at': user_role.assigned_at,
                'expires_at': user_role.expires_at,
                'is_expired': user_role.is_expired,
            })

        return roles_data

    def get_user_permissions(self, obj):
        """
        Return aggregated permissions from all user's roles.
        """
        user = getattr(obj, 'user', None)
        if not user:
            return []

        # If superuser, they have all permissions
        if user.is_superuser:
            return ['*']  # Wildcard indicates all permissions

        # Aggregate permissions from all active roles
        permissions = set()
        user_roles = UserRole.objects.all_colleges().filter(
            user=user,
            is_active=True
        ).select_related('role')

        for user_role in user_roles:
            if user_role.role.permissions:
                # Permissions stored as JSONField
                if isinstance(user_role.role.permissions, list):
                    permissions.update(user_role.role.permissions)
                elif isinstance(user_role.role.permissions, dict):
                    permissions.update(user_role.role.permissions.keys())

        return sorted(list(permissions))

    def get_user_profile(self, obj):
        """
        Return the user's profile information if it exists.
        """
        user = getattr(obj, 'user', None)
        if not user:
            return None

        try:
            profile = UserProfile.objects.all_colleges().get(user=user, is_active=True)
            return {
                'id': profile.id,
                'department_id': profile.department_id,
                'department_name': profile.department.name if profile.department else None,
                'address_line1': profile.address_line1,
                'address_line2': profile.address_line2,
                'city': profile.city,
                'state': profile.state,
                'pincode': profile.pincode,
                'country': profile.country,
                'emergency_contact_name': profile.emergency_contact_name,
                'emergency_contact_phone': profile.emergency_contact_phone,
                'emergency_contact_relation': profile.emergency_contact_relation,
                'blood_group': profile.blood_group,
                'nationality': profile.nationality,
                'religion': profile.religion,
                'caste': profile.caste,
                'linkedin_url': profile.linkedin_url,
                'website_url': profile.website_url,
                'bio': profile.bio,
            }
        except UserProfile.DoesNotExist:
            return None


# ============================================================================
# ROLE SERIALIZERS
# ============================================================================


class RoleListSerializer(serializers.ModelSerializer):
    """Serializer for listing roles (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = Role
        fields = [
            'id', 'code', 'name',
            'college', 'college_name',
            'display_order', 'is_active'
        ]
        read_only_fields = ['id', 'college_name']


class RoleSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Role model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = Role
        fields = [
            'id', 'college', 'college_name',
            'name', 'code', 'description', 'permissions',
            'display_order', 'is_active',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]

    def validate_code(self, value):
        """Ensure role code is unique within college."""
        instance = self.instance
        college = self.initial_data.get('college') or (instance.college_id if instance else None)

        query = Role.objects.filter(code=value, college_id=college)
        if instance:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            raise serializers.ValidationError("Role with this code already exists in this college.")
        return value.upper()


# ============================================================================
# USER ROLE SERIALIZERS
# ============================================================================


class UserRoleSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for UserRole assignments."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserRole
        fields = [
            'id', 'college', 'college_name',
            'user', 'user_name',
            'role', 'role_name',
            'assigned_by', 'assigned_by_name',
            'assigned_at', 'expires_at',
            'is_expired', 'is_active',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'user_name', 'role_name',
            'assigned_by_name', 'assigned_at', 'is_expired',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        """Validate user role assignment."""
        user = attrs.get('user')
        role = attrs.get('role')
        college = attrs.get('college')

        if user.college_id and user.college_id != college.id:
            raise serializers.ValidationError({
                'user': 'User must belong to the same college.'
            })

        if role.college_id != college.id:
            raise serializers.ValidationError({
                'role': 'Role must belong to the same college.'
            })

        return attrs


# ============================================================================
# DEPARTMENT SERIALIZERS
# ============================================================================


class DepartmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing departments (minimal fields)."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    hod_name = serializers.CharField(source='hod.get_full_name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'short_name',
            'college', 'college_name',
            'hod', 'hod_name',
            'display_order', 'is_active'
        ]
        read_only_fields = ['id', 'college_name', 'hod_name']


class DepartmentSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Department model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    hod_name = serializers.CharField(source='hod.get_full_name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'college', 'college_name',
            'code', 'name', 'short_name', 'description',
            'hod', 'hod_name',
            'display_order', 'is_active',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'hod_name',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]

    def validate_code(self, value):
        """Ensure department code is unique within college."""
        instance = self.instance
        college = self.initial_data.get('college') or (instance.college_id if instance else None)

        query = Department.objects.filter(code=value, college_id=college)
        if instance:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            raise serializers.ValidationError("Department with this code already exists in this college.")
        return value.upper()


# ============================================================================
# USER PROFILE SERIALIZERS
# ============================================================================


class UserProfileSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for UserProfile model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'college', 'college_name',
            'user', 'user_name',
            'department', 'department_name',
            'address_line1', 'address_line2', 'city', 'state', 'pincode', 'country',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'blood_group', 'nationality', 'religion', 'caste',
            'profile_data',
            'linkedin_url', 'website_url', 'bio',
            'is_active',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name', 'user_name', 'department_name',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        """Validate profile belongs to the same college as the user."""
        user = attrs.get('user')
        college = attrs.get('college')

        if user.college_id and user.college_id != college.id:
            raise serializers.ValidationError({
                'user': 'Profile must belong to the same college as the user.'
            })

        return attrs


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================


class BulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk delete operations."""
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of UUIDs to delete"
    )


class BulkActivateSerializer(serializers.Serializer):
    """Serializer for bulk activate/deactivate operations."""
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of UUIDs to activate/deactivate"
    )
    is_active = serializers.BooleanField(help_text="Set active status")


class BulkUserTypeUpdateSerializer(serializers.Serializer):
    """Serializer for bulk user type updates."""
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of user UUIDs"
    )
    user_type = serializers.ChoiceField(
        choices=UserType.choices,
        help_text="New user type"
    )
