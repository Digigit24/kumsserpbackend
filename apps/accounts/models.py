"""
Accounts models for the KUMSS ERP system.
Provides authentication, authorization, and user management.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from apps.core.models import AuditModel, TimeStampedModel, CollegeScopedModel, College
from apps.core.managers import CollegeManager
from .managers import UserManager


# ============================================================================
# USER TYPE ENUM
# ============================================================================


class UserType(models.TextChoices):
    """User type categorization for high-level access control."""
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    COLLEGE_ADMIN = 'college_admin', 'College Admin'
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'
    PARENT = 'parent', 'Parent'
    STAFF = 'staff', 'Support Staff'
    STORE_MANAGER = 'store_manager', 'Store Manager'


class GenderChoices(models.TextChoices):
    """Gender options."""
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'


# ============================================================================
# USER MODEL
# ============================================================================


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom user model for the KUMSS system.
    Supports multi-college tenancy and various user types.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique user identifier (UUID)"
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="Unique username for authentication"
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text="User email address"
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Contact phone number"
    )

    # Profile fields
    first_name = models.CharField(
        max_length=100,
        help_text="First name"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Last name"
    )
    middle_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Middle name"
    )
    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
        null=True,
        blank=True,
        help_text="Gender"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Date of birth"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="User avatar image"
    )

    # College association
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        help_text="Primary college affiliation (null for super admins)"
    )

    # User type and permissions
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.STUDENT,
        db_index=True,
        help_text="User role/type in the system"
    )

    # Status fields
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Designates whether this user should be treated as active"
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into admin site"
    )
    is_superadmin = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Superadmin has access to all colleges and all permissions"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Indicates if the email/phone is verified"
    )

    # Authentication tracking
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of last login"
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Count of consecutive failed login attempts"
    )
    lockout_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this time"
    )

    # Important dates
    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text="Date when the user registered"
    )
    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last password change"
    )

    # Manager
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['college']),
            models.Index(fields=['user_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['college', 'user_type']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def get_full_name(self):
        """Return the full name of the user."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def is_locked_out(self):
        """Check if the user account is currently locked."""
        if self.lockout_until and self.lockout_until > timezone.now():
            return True
        return False

    def increment_failed_login(self):
        """Increment failed login attempts and lock account if threshold exceeded."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.lockout_until = timezone.now() + timedelta(minutes=30)
        self.save(update_fields=['failed_login_attempts', 'lockout_until'])

    def reset_failed_login(self):
        """Reset failed login attempts after successful login."""
        self.failed_login_attempts = 0
        self.lockout_until = None
        self.save(update_fields=['failed_login_attempts', 'lockout_until'])


# ============================================================================
# ROLE MODEL
# ============================================================================


class Role(CollegeScopedModel):
    """
    Roles for fine-grained access control within a college.
    Examples: HOD, Class Coordinator, Exam Controller, etc.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text="College this role belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Role name (e.g., 'HOD', 'Class Coordinator')"
    )
    code = models.CharField(
        max_length=50,
        help_text="Unique role code"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Role description"
    )
    permissions = models.JSONField(
        default=dict,
        help_text="Permission set for this role (module-level access)"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Display order in UI"
    )

    class Meta:
        db_table = 'role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'code'],
                name='unique_college_role_code'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.college.short_name})"


# ============================================================================
# USER ROLE ASSIGNMENT
# ============================================================================


class UserRole(CollegeScopedModel):
    """
    Many-to-many relationship between users and roles with additional metadata.
    Allows users to have multiple roles within a college.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='user_roles',
        help_text="Associated college"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        help_text="User assigned to the role"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        help_text="Role assigned to the user"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='role_assignments_made',
        help_text="User who made this assignment"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the role was assigned"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Role expiration date (null = no expiration)"
    )

    class Meta:
        db_table = 'user_role'
        verbose_name = 'User Role Assignment'
        verbose_name_plural = 'User Role Assignments'
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['user']),
            models.Index(fields=['role']),
            models.Index(fields=['college', 'user']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'user', 'role'],
                name='unique_college_user_role'
            )
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.name}"

    def is_expired(self):
        """Check if this role assignment has expired."""
        if self.expires_at and self.expires_at < timezone.now():
            return True
        return False

    def clean(self):
        """Validate that user, role, and college are aligned."""
        if self.user.college_id and self.user.college_id != self.college_id:
            raise ValidationError("User must belong to the same college as the role.")
        if self.role.college_id != self.college_id:
            raise ValidationError("Role must belong to the same college.")


# ============================================================================
# DEPARTMENT MODEL
# ============================================================================


class Department(CollegeScopedModel):
    """
    Academic departments within a college.
    Examples: Computer Science, Mechanical Engineering, etc.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='departments',
        help_text="Owning college"
    )
    code = models.CharField(
        max_length=20,
        help_text="Department code (e.g., 'CS', 'ME')"
    )
    name = models.CharField(
        max_length=200,
        help_text="Department name"
    )
    short_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Abbreviated name"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Department description"
    )
    hod = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments_as_hod',
        help_text="Head of Department"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Display order in UI"
    )

    class Meta:
        db_table = 'department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'code'],
                name='unique_college_department_code'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.college.short_name})"


# ============================================================================
# USER PROFILE (EXTENDED USER DATA)
# ============================================================================


class UserProfile(CollegeScopedModel):
    """
    Extended profile information for users.
    Stores additional data specific to user types (teacher, student, etc.)
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='user_profiles',
        help_text="Associated college"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Associated user"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        help_text="Department affiliation"
    )

    # Address information
    address_line1 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Address line 1"
    )
    address_line2 = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Address line 2"
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="City"
    )
    state = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="State/Province"
    )
    pincode = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Postal/ZIP code"
    )
    country = models.CharField(
        max_length=100,
        default='India',
        help_text="Country"
    )

    # Emergency contact
    emergency_contact_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Emergency contact person name"
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Emergency contact phone"
    )
    emergency_contact_relation = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Relationship to emergency contact"
    )

    # Additional fields
    blood_group = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        help_text="Blood group (e.g., 'A+', 'O-')"
    )
    nationality = models.CharField(
        max_length=100,
        default='Indian',
        help_text="Nationality"
    )
    religion = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Religion"
    )
    caste = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Caste category"
    )

    # Professional/Academic data (flexible JSON)
    profile_data = models.JSONField(
        default=dict,
        help_text="Additional profile data specific to user type"
    )

    # Social links
    linkedin_url = models.URLField(
        null=True,
        blank=True,
        help_text="LinkedIn profile URL"
    )
    website_url = models.URLField(
        null=True,
        blank=True,
        help_text="Personal website URL"
    )

    # Bio
    bio = models.TextField(
        null=True,
        blank=True,
        help_text="User biography"
    )

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['user']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"

    def clean(self):
        """Validate profile belongs to the same college as the user."""
        if self.user.college_id and self.user.college_id != self.college_id:
            raise ValidationError("Profile must belong to the same college as the user.")
