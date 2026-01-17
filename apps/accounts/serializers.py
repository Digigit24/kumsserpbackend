"""
DRF Serializers for Accounts app models.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
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
    college_name = serializers.SerializerMethodField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    teacher_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name',
            'user_type', 'user_type_display',
            'college', 'college_name',
            'teacher_id',
            'is_active', 'is_verified', 'date_joined'
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.UUIDField(allow_null=True))
    def get_teacher_id(self, obj):
        """Get teacher profile ID if user is a teacher."""
        if hasattr(obj, 'teacher_profile') and obj.teacher_profile:
            return obj.teacher_profile.id
        return None

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_college_name(self, obj):
        """Get college name with robust fallbacks."""
        # 1. Try direct relationship
        if obj.college:
            return obj.college.name
            
        # 2. Try fetching by college_id if it exists on the user object
        if obj.college_id:
            try:
                from apps.core.models import College
                return College.objects.values_list('name', flat=True).get(id=obj.college_id)
            except (ValueError, Exception):
                pass
        
        # 3. Fallback to context (X-College-Id header) as a last resort
        request = self.context.get('request')
        if request:
            college_id = request.headers.get('X-College-Id')
            if college_id and str(college_id).lower() != 'all':
                try:
                    from apps.core.models import College
                    return College.objects.values_list('name', flat=True).get(id=college_id)
                except (ValueError, Exception):
                    pass
        return None


class UserSerializer(serializers.ModelSerializer):
    """Full serializer for User model with all fields."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    college_name = serializers.SerializerMethodField()
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)

    # Add teacher_id and student_id for easy reference
    teacher_id = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'first_name', 'last_name', 'middle_name', 'full_name',
            'gender', 'gender_display', 'date_of_birth', 'avatar',
            'college', 'college_name',
            'user_type', 'user_type_display',
            'teacher_id', 'student_id',  # Added for frontend convenience
            'is_active', 'is_staff', 'is_verified',
            'last_login', 'last_login_ip',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'college_name', 'user_type_display', 'gender_display',
            'teacher_id', 'student_id',
            'last_login', 'last_login_ip', 'date_joined',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_college_name(self, obj):
        """Get college name with robust fallbacks."""
        # 1. Try direct relationship
        if obj.college:
            return obj.college.name
            
        # 2. Try fetching by college_id if it exists on the user object
        if obj.college_id:
            try:
                from apps.core.models import College
                return College.objects.values_list('name', flat=True).get(id=obj.college_id)
            except (ValueError, Exception):
                pass
        
        # 3. Fallback to context (X-College-Id header) as a last resort
        # This is strictly for cases where user has NO college assigned but we are viewing them in a college context
        request = self.context.get('request')
        if request:
            college_id = request.headers.get('X-College-Id')
            if college_id and str(college_id).lower() != 'all':
                try:
                    from apps.core.models import College
                    return College.objects.values_list('name', flat=True).get(id=college_id)
                except (ValueError, Exception):
                    pass
        return None

    @extend_schema_field(serializers.UUIDField(allow_null=True))
    def get_teacher_id(self, obj):
        """Get teacher profile ID if user is a teacher."""
        if hasattr(obj, 'teacher_profile') and obj.teacher_profile:
            return obj.teacher_profile.id
        return None

    @extend_schema_field(serializers.UUIDField(allow_null=True))
    def get_student_id(self, obj):
        """Get student profile ID if user is a student."""
        if hasattr(obj, 'student_profile') and obj.student_profile:
            return obj.student_profile.id
        return None

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
    student_profile = serializers.DictField(write_only=True, required=False)
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
            'college', 'user_type', 'is_active',
            'student_profile'
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
        student_profile = validated_data.pop('student_profile', None) or {}
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        with transaction.atomic():
            user = User.objects.create_user(password=password, **validated_data)
            if user.user_type == UserType.STUDENT:
                self._create_student_profile(user, student_profile)
        return user

    def to_representation(self, instance):
        """Return the full user details in the response."""
        return UserSerializer(instance, context=self.context).data

    def _create_student_profile(self, user, student_profile):
        from apps.students.models import Student
        from apps.academic.models import Program
        from apps.core.models import AcademicYear

        if Student.objects.all_colleges().filter(user=user).exists():
            return

        college_id = student_profile.get('college') or user.college_id
        if not college_id:
            raise serializers.ValidationError({
                'student_profile': 'College is required to create a student profile.'
            })

        program_id = student_profile.get('program')
        if program_id:
            program = Program.objects.all_colleges().filter(id=program_id).first()
        else:
            program = Program.objects.all_colleges().filter(college_id=college_id).order_by('id').first()
        if not program:
            raise serializers.ValidationError({
                'student_profile': 'Program is required to create a student profile.'
            })

        academic_year_id = student_profile.get('academic_year')
        if academic_year_id:
            academic_year = AcademicYear.objects.all_colleges().filter(id=academic_year_id).first()
        else:
            academic_year = AcademicYear.objects.all_colleges().filter(
                college_id=college_id,
                is_current=True
            ).first()
            if not academic_year:
                academic_year = AcademicYear.objects.all_colleges().filter(
                    college_id=college_id
                ).order_by('-start_date').first()
        if not academic_year:
            raise serializers.ValidationError({
                'student_profile': 'Academic year is required to create a student profile.'
            })

        admission_date = student_profile.get('admission_date') or timezone.now().date()
        admission_type = student_profile.get('admission_type') or 'regular'

        college = College.objects.all_colleges().filter(id=college_id).first()
        if not college:
            raise serializers.ValidationError({
                'student_profile': 'Invalid college for student profile.'
            })

        admission_number = student_profile.get('admission_number')
        registration_number = student_profile.get('registration_number')
        if not admission_number or not registration_number:
            year = admission_date.year
            count = Student.objects.all_colleges().filter(college_id=college_id).count() + 1
            if not admission_number:
                admission_number = f"ADM-{college.code}-{year}-{count:05d}"
            if not registration_number:
                registration_number = f"REG-{college.code}-{year}-{count:05d}"

        first_name = student_profile.get('first_name') or user.first_name
        last_name = student_profile.get('last_name') or user.last_name
        email = student_profile.get('email') or user.email
        gender = student_profile.get('gender') or user.gender
        date_of_birth = student_profile.get('date_of_birth') or user.date_of_birth

        missing = []
        if not first_name:
            missing.append('first_name')
        if not last_name:
            missing.append('last_name')
        if not email:
            missing.append('email')
        if not gender:
            missing.append('gender')
        if not date_of_birth:
            missing.append('date_of_birth')
        if missing:
            raise serializers.ValidationError({
                'student_profile': f"Missing required fields: {', '.join(missing)}"
            })

        request = self.context.get('request')
        actor = getattr(request, 'user', None)

        Student.objects.create(
            user=user,
            college_id=college_id,
            admission_number=admission_number,
            admission_date=admission_date,
            admission_type=admission_type,
            roll_number=student_profile.get('roll_number'),
            registration_number=registration_number,
            program=program,
            current_class_id=student_profile.get('current_class'),
            current_section_id=student_profile.get('current_section'),
            academic_year=academic_year,
            category_id=student_profile.get('category'),
            group_id=student_profile.get('group'),
            first_name=first_name,
            middle_name=student_profile.get('middle_name') or user.middle_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            blood_group=student_profile.get('blood_group'),
            email=email,
            phone=student_profile.get('phone') or user.phone,
            alternate_phone=student_profile.get('alternate_phone'),
            nationality=student_profile.get('nationality') or 'Indian',
            religion=student_profile.get('religion'),
            caste=student_profile.get('caste'),
            mother_tongue=student_profile.get('mother_tongue'),
            aadhar_number=student_profile.get('aadhar_number'),
            pan_number=student_profile.get('pan_number'),
            is_active=student_profile.get('is_active', True),
            is_alumni=student_profile.get('is_alumni', False),
            created_by=actor,
            updated_by=actor,
        )
        # Use selective cache invalidation for student data
        try:
            patterns = ['*student*', '*user*', '*account*']
            for pattern in patterns:
                try:
                    keys = cache.keys(pattern)
                    if keys:
                        cache.delete_many(keys)
                except:
                    pass
        except Exception:
            pass


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


class CustomPasswordChangeSerializer(serializers.Serializer):
    """Serializer for custom password change with confirmation."""
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


class TokenWithUserSerializer(DRATokenSerializer):
    """
    Enhanced token serializer that returns comprehensive user details,
    primary college ID, and all accessible college IDs for multi-tenancy support.
    Includes user roles, permissions, and complete profile information.
    """
    message = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    college_id = serializers.SerializerMethodField()
    tenant_ids = serializers.SerializerMethodField()
    accessible_colleges = serializers.SerializerMethodField()
    user_roles = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    class Meta(DRATokenSerializer.Meta):
        fields = [
            'key',
            'message',
            'user',
            'college_id',
            'tenant_ids',
            'accessible_colleges',
            'user_roles',
            'user_permissions',
            'user_profile'
        ]

    @extend_schema_field(serializers.CharField())
    def get_message(self, obj):
        """Return a success message."""
        user = getattr(obj, 'user', None)
        if user:
            return f"Welcome back, {user.get_full_name()}! Login successful."
        return "Login successful"

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_college_id(self, obj):
        """Return the user's primary college ID."""
        user = getattr(obj, 'user', None)
        if not user:
            return None
        if not getattr(user, 'college_id', None) and (user.is_superuser or user.is_staff):
            # Superusers/staff without a college get sentinel 0 for frontend handling
            return 0
        return user.college_id

    @extend_schema_field(serializers.ListField(child=serializers.IntegerField()))
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

    @extend_schema_field(CollegeBasicSerializer(many=True))
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

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_user_roles(self, obj):
        """
        Return all active roles assigned to the user.
        Includes both the user's primary user_type and any additional UserRole assignments.
        """
        user = getattr(obj, 'user', None)
        if not user:
            return []

        roles_data = []

        # Add the user's primary user_type as the base role
        if user.user_type:
            roles_data.append({
                'id': None,  # No specific role assignment ID for user_type
                'role_id': None,
                'role_name': user.get_user_type_display(),
                'role_code': user.user_type,
                'college_id': user.college_id,
                'college_name': user.college.short_name if user.college else None,
                'is_primary': True,  # Mark this as the primary role
                'assigned_at': user.date_joined,
                'expires_at': None,
                'is_expired': False,
            })

        # Get all active roles for the user (using all_colleges to bypass scoping)
        user_roles = UserRole.objects.all_colleges().filter(
            user=user,
            is_active=True
        ).select_related('role', 'college')

        for user_role in user_roles:
            roles_data.append({
                'id': user_role.id,
                'role_id': user_role.role.id,
                'role_name': user_role.role.name,
                'role_code': user_role.role.code,
                'college_id': user_role.college_id,
                'college_name': user_role.college.short_name if user_role.college else None,
                'is_primary': False,  # Additional role
                'assigned_at': user_role.assigned_at,
                'expires_at': user_role.expires_at,
                'is_expired': user_role.is_expired,
            })

        return roles_data

    @extend_schema_field(serializers.DictField())
    def get_user_permissions(self, obj):
        """
        Return user permissions using the new KUMSS permission system.
        Returns comprehensive permission JSON with scope and enabled status for each resource/action.
        """
        user = getattr(obj, 'user', None)
        if not user:
            return {}

        # Import the permission manager from the new system
        from apps.core.permissions.manager import get_user_permissions as get_perms
        from apps.core.models import College

        # Get user's college for permission lookup
        college = None
        if user.college_id:
            try:
                college = College.objects.all_colleges().get(id=user.college_id)
            except College.DoesNotExist:
                pass

        # Get permissions from the new system
        # This returns the full permission JSON structure with scope and enabled for each action
        permissions = get_perms(user, college)

        return permissions

    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_user_profile(self, obj):
        """
        Return the user's profile information if it exists.
        Includes teacher_id for teacher users and student_id for student users.
        """
        user = getattr(obj, 'user', None)
        if not user:
            return None

        profile_data = {}

        # Add teacher ID if user is a teacher
        try:
            from apps.teachers.models import Teacher
            teacher = Teacher.objects.all_colleges().get(user=user, is_active=True)
            profile_data['teacher_id'] = teacher.id
            profile_data['employee_id'] = teacher.employee_id
        except (Teacher.DoesNotExist, Exception):
            pass

        # Add student ID if user is a student
        try:
            from apps.students.models import Student
            student = Student.objects.all_colleges().get(user=user, is_active=True)
            profile_data['student_id'] = student.id
            profile_data['admission_number'] = student.admission_number
        except (Student.DoesNotExist, Exception):
            pass

        # Add UserProfile data if it exists
        try:
            profile = UserProfile.objects.all_colleges().get(user=user, is_active=True)
            profile_data.update({
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
            })
        except (UserProfile.DoesNotExist, Exception):
            pass

        return profile_data if profile_data else None


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
            'parent', 'is_organizational_position', 'level',
            'display_order', 'is_active',
            'created_by_name', 'updated_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'college_name',
            'level',
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

class RoleTreeSerializer(serializers.ModelSerializer):
    """Serializer for nested role hierarchy tree."""
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description',
            'parent', 'parent_name', 'level',
            'is_organizational_position', 'children'
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('display_order', 'name')
        return RoleTreeSerializer(children, many=True).data


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
    college_name = serializers.CharField(source='college.name', read_only=True)
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


class UserBulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk user delete operations (uses UUIDs)."""
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of user UUIDs to delete"
    )


class UserBulkActivateSerializer(serializers.Serializer):
    """Serializer for bulk user activate/deactivate operations (uses UUIDs)."""
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of user UUIDs to activate/deactivate"
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
