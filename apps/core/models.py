"""
Core models for the KUMSS ERP system.
Provides system-wide settings, colleges, and base configurations.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .managers import CollegeManager
from .utils import get_current_college_id


# ============================================================================
# ABSTRACT BASE MODELS
# ============================================================================


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.
    All models should inherit from this to track creation and modification times.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class AuditModel(TimeStampedModel):
    """
    Abstract base model that extends TimeStampedModel with audit fields.
    Provides soft-delete functionality and audit trail support.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Indicates if the record is active (soft delete)"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft delete the record by setting is_active to False."""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted record by setting is_active to True."""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])


class CollegeScopedModel(AuditModel):
    """
    Abstract base model that scopes records by college ID.
    """
    objects = CollegeManager()

    class Meta:
        abstract = True

    def ensure_college(self):
        """
        Ensure a college_id exists for models that carry a college FK.
        """
        if hasattr(self, 'college_id') and not self.college_id:
            college_id = get_current_college_id()
            if not college_id:
                raise ValidationError("College is required. Provide X-College-ID header or include 'college' in the payload.")
            self.college_id = college_id

    def save(self, *args, **kwargs):
        self.ensure_college()
        super().save(*args, **kwargs)


# Backward-compatibility alias
TenantModel = CollegeScopedModel


# ============================================================================
class College(CollegeScopedModel):
    """
    Represents a college/institution in the college-scoped system.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Unique college code"
    )
    name = models.CharField(
        max_length=200,
        help_text="Full name of the college"
    )
    short_name = models.CharField(
        max_length=50,
        help_text="Abbreviated name"
    )
    email = models.EmailField(
        help_text="Contact email address"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Contact phone number"
    )
    website = models.URLField(
        null=True,
        blank=True,
        help_text="College website URL"
    )

    # Address fields
    address_line1 = models.CharField(
        max_length=255,
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
        help_text="City"
    )
    state = models.CharField(
        max_length=100,
        help_text="State/Province"
    )
    pincode = models.CharField(
        max_length=10,
        help_text="Postal/ZIP code"
    )
    country = models.CharField(
        max_length=100,
        default='India',
        help_text="Country"
    )

    # Additional information
    logo = models.ImageField(
        upload_to='college_logos/',
        null=True,
        blank=True,
        help_text="College logo (stored in S3)"
    )
    established_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of establishment"
    )
    affiliation_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Official affiliation identifier"
    )

    # Branding
    primary_color = models.CharField(
        max_length=7,
        default='#1976d2',
        help_text="Primary brand color (hex format)"
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#dc004e',
        help_text="Secondary brand color (hex format)"
    )

    # Configuration
    settings = models.JSONField(
        null=True,
        blank=True,
        help_text="College-specific settings (academic, fees, notifications, theme)"
    )
    is_main = models.BooleanField(
        default=False,
        help_text="Indicates if this is the main university"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Display order in UI"
    )

    class Meta:
        db_table = 'college'
        verbose_name = 'College'
        verbose_name_plural = 'Colleges'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['display_order']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class AcademicYear(CollegeScopedModel):
    """
    Represents an academic year/session.
    Only one academic year can be current per college.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='academic_years',
        help_text="Owning college"
    )
    year = models.CharField(
        max_length=20,
        help_text="Academic year label (e.g., '2025-2026')"
    )
    start_date = models.DateField(
        help_text="Academic year start date"
    )
    end_date = models.DateField(
        help_text="Academic year end date"
    )
    is_current = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates if this is the current academic year"
    )

    class Meta:
        db_table = 'academic_year'
        verbose_name = 'Academic Year'
        verbose_name_plural = 'Academic Years'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['year']),
            models.Index(fields=['is_current']),
            models.Index(fields=['college', 'is_current']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'year'],
                name='unique_college_academic_year'
            )
        ]

    def __str__(self):
        return self.year

    def clean(self):
        """Validate that end_date is after start_date."""
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")


class AcademicSession(CollegeScopedModel):
    """
    Represents a specific academic session (semester) within an academic year.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='academic_sessions',
        help_text="Associated college"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="Associated academic year"
    )
    name = models.CharField(
        max_length=100,
        help_text="Session name"
    )
    semester = models.IntegerField(
        help_text="Semester number (1-8)"
    )
    start_date = models.DateField(
        help_text="Session start date"
    )
    end_date = models.DateField(
        help_text="Session end date"
    )
    is_current = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates if this is the current session"
    )

    class Meta:
        db_table = 'academic_session'
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['academic_year']),
            models.Index(fields=['is_current']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'academic_year', 'semester'],
                name='unique_college_year_semester'
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.academic_year.year}"

    def clean(self):
        """Validate semester number and dates."""
        if self.semester not in range(1, 9):
            raise ValidationError("Semester must be between 1 and 8.")
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")
        if self.academic_year and self.college and self.academic_year.college_id != self.college_id:
            raise ValidationError("Academic year must belong to the same college as the session.")


class Holiday(CollegeScopedModel):
    """
    Represents holidays for a college.
    """
    HOLIDAY_TYPE_CHOICES = [
        ('national', 'National Holiday'),
        ('festival', 'Festival'),
        ('college', 'College Holiday'),
        ('exam', 'Exam Holiday'),
    ]

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='holidays',
        help_text="Associated college"
    )
    name = models.CharField(
        max_length=200,
        help_text="Name of the holiday"
    )
    date = models.DateField(
        db_index=True,
        help_text="Holiday date"
    )
    holiday_type = models.CharField(
        max_length=20,
        choices=HOLIDAY_TYPE_CHOICES,
        help_text="Type of holiday"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Additional details about the holiday"
    )

    class Meta:
        db_table = 'holiday'
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
        ordering = ['date']
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['date']),
            models.Index(fields=['college', 'date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.date}"


class Weekend(CollegeScopedModel):
    """
    Defines weekend days for a college.
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='weekends',
        help_text="Associated college"
    )
    day = models.IntegerField(
        choices=DAY_CHOICES,
        help_text="Day of the week (0=Monday, 6=Sunday)"
    )

    class Meta:
        db_table = 'weekend'
        verbose_name = 'Weekend'
        verbose_name_plural = 'Weekends'
        ordering = ['day']
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['college', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['college', 'day'],
                name='unique_college_weekend_day'
            )
        ]

    def __str__(self):
        return f"{self.college.short_name} - {self.get_day_display()}"


class SystemSetting(CollegeScopedModel):
    """
    System-wide settings for a college.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='system_settings',
        help_text="Owning college"
    )
    settings = models.JSONField(
        help_text="System settings (system, email, sms, security, features)"
    )

    class Meta:
        db_table = 'system_setting'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['college', 'is_active']),
        ]

    def __str__(self):
        return f"System Settings - {self.college.name if self.college else 'Unknown'}"


class NotificationSetting(CollegeScopedModel):
    """
    Notification configuration for a college.
    Supports SMS, Email, and WhatsApp gateways.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        help_text="Associated college"
    )

    # SMS Configuration
    sms_enabled = models.BooleanField(
        default=True,
        help_text="Enable SMS notifications"
    )
    sms_gateway = models.CharField(
        max_length=50,
        default='twilio',
        help_text="SMS gateway provider"
    )
    sms_api_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Encrypted SMS API key"
    )
    sms_sender_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="SMS sender ID"
    )

    # Email Configuration
    email_enabled = models.BooleanField(
        default=True,
        help_text="Enable email notifications"
    )
    email_gateway = models.CharField(
        max_length=50,
        default='sendgrid',
        help_text="Email gateway provider"
    )
    email_api_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Encrypted email API key"
    )
    email_from = models.EmailField(
        null=True,
        blank=True,
        help_text="Sender email address"
    )

    # WhatsApp Configuration
    whatsapp_enabled = models.BooleanField(
        default=False,
        help_text="Enable WhatsApp notifications"
    )
    whatsapp_api_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Encrypted WhatsApp API key"
    )
    whatsapp_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="WhatsApp sender number"
    )

    # Notification Preferences
    attendance_notif = models.BooleanField(
        default=True,
        help_text="Enable attendance notifications"
    )
    fee_reminder = models.BooleanField(
        default=True,
        help_text="Enable fee reminders"
    )
    fee_days = models.CharField(
        max_length=50,
        default='7,3,1',
        help_text="Days before due date to send fee reminders (CSV)"
    )

    # Advanced Configuration
    notif_settings = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional notification configurations (channels, schedules)"
    )

    class Meta:
        db_table = 'notification_setting'
        verbose_name = 'Notification Setting'
        verbose_name_plural = 'Notification Settings'
        indexes = [
            models.Index(fields=['college']),
            models.Index(fields=['college', 'is_active']),
        ]

    def __str__(self):
        return f"Notification Settings - {self.college.short_name}"


class ActivityLog(models.Model):
    """
    Tracks all system activities for audit purposes, scoped by college.
    """
    objects = CollegeManager()

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('download', 'Download'),
        ('upload', 'Upload'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        help_text="User who performed the action"
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text="Associated college"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    model_name = models.CharField(
        max_length=100,
        help_text="Name of the model/entity affected"
    )
    object_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID of the affected record"
    )
    description = models.TextField(
        help_text="Human-readable description of the action"
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional data (changes, request info, etc.)"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Browser/client user agent"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action occurred"
    )

    class Meta:
        db_table = 'activity_log'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['college']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['college', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} - {self.model_name} by {self.user} at {self.timestamp}"
