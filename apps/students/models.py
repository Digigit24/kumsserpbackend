"""
Student models for the KUMSS ERP system.
Provides student information, admission, documents, and related data.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import CollegeScopedModel, AuditModel, TimeStampedModel, College, AcademicYear
from apps.academic.models import Program, Class, Section, Subject


class StudentCategory(CollegeScopedModel):
    """
    Represents student categories (e.g., General, OBC, SC, ST).
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='student_categories',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Category name")
    code = models.CharField(max_length=20, help_text="Category code")
    description = models.TextField(null=True, blank=True, help_text="Description")

    class Meta:
        db_table = 'student_category'
        verbose_name = 'Student Category'
        verbose_name_plural = 'Student Categories'
        unique_together = ['college', 'code']
        indexes = [
            models.Index(fields=['college', 'code']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class StudentGroup(CollegeScopedModel):
    """
    Represents student groups (e.g., Morning Batch, Evening Batch).
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='student_groups',
        help_text="College reference"
    )
    name = models.CharField(max_length=100, help_text="Group name")
    description = models.TextField(null=True, blank=True, help_text="Description")

    class Meta:
        db_table = 'student_group'
        verbose_name = 'Student Group'
        verbose_name_plural = 'Student Groups'
        indexes = [
            models.Index(fields=['college']),
        ]

    def __str__(self):
        return self.name


class Student(CollegeScopedModel):
    """
    Represents a student in the system.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="User account"
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='students',
        help_text="College reference"
    )
    admission_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Admission number"
    )
    admission_date = models.DateField(help_text="Admission date")
    admission_type = models.CharField(max_length=20, help_text="Admission type")
    roll_number = models.CharField(max_length=50, null=True, blank=True, help_text="Roll number")
    registration_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Registration number"
    )
    
    # Academic details
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name='students',
        help_text="Program"
    )
    current_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_students',
        help_text="Current class"
    )
    current_section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_students',
        help_text="Current section"
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='students',
        help_text="Academic year"
    )
    category = models.ForeignKey(
        StudentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Category"
    )
    group = models.ForeignKey(
        StudentGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Group"
    )

    # Personal details
    first_name = models.CharField(max_length=100, help_text="First name")
    middle_name = models.CharField(max_length=100, null=True, blank=True, help_text="Middle name")
    last_name = models.CharField(max_length=100, help_text="Last name")
    date_of_birth = models.DateField(help_text="Date of birth")
    gender = models.CharField(max_length=10, help_text="Gender")
    blood_group = models.CharField(max_length=5, null=True, blank=True, help_text="Blood group")
    email = models.EmailField(help_text="Email")
    phone = models.CharField(max_length=20, null=True, blank=True, help_text="Phone")
    alternate_phone = models.CharField(max_length=20, null=True, blank=True, help_text="Alternate phone")
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True, help_text="Photo")

    # Identity details
    nationality = models.CharField(max_length=100, default='Indian', help_text="Nationality")
    religion = models.CharField(max_length=100, null=True, blank=True, help_text="Religion")
    caste = models.CharField(max_length=100, null=True, blank=True, help_text="Caste")
    mother_tongue = models.CharField(max_length=100, null=True, blank=True, help_text="Mother tongue")
    aadhar_number = models.CharField(max_length=12, null=True, blank=True, help_text="Aadhar number")
    pan_number = models.CharField(max_length=10, null=True, blank=True, help_text="PAN number")

    # Status
    is_alumni = models.BooleanField(default=False, help_text="Alumni flag")
    disabled_date = models.DateField(null=True, blank=True, help_text="Disabled date")
    disable_reason = models.TextField(null=True, blank=True, help_text="Disable reason")

    # Optional subjects
    optional_subjects = models.ManyToManyField(
        Subject,
        blank=True,
        related_name='students',
        help_text="Optional subjects"
    )

    # Custom fields (JSON)
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom student fields defined on frontend"
    )

    class Meta:
        db_table = 'student'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        unique_together = ['college', 'admission_number']
        indexes = [
            models.Index(fields=['college', 'admission_number']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['current_class', 'current_section']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.admission_number})"

    def get_full_name(self):
        """Return the full name of the student."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class Guardian(TimeStampedModel):
    """
    Represents a guardian (parent/guardian) of students.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='guardian_profile',
        help_text="User account"
    )
    first_name = models.CharField(max_length=100, help_text="First name")
    middle_name = models.CharField(max_length=100, null=True, blank=True, help_text="Middle name")
    last_name = models.CharField(max_length=100, help_text="Last name")
    relation = models.CharField(max_length=20, help_text="Relation type (father/mother/guardian)")
    email = models.EmailField(null=True, blank=True, help_text="Email")
    phone = models.CharField(max_length=20, db_index=True, help_text="Phone")
    alternate_phone = models.CharField(max_length=20, null=True, blank=True, help_text="Alternate phone")
    occupation = models.CharField(max_length=200, null=True, blank=True, help_text="Occupation")
    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual income"
    )
    address = models.TextField(null=True, blank=True, help_text="Address")
    photo = models.ImageField(upload_to='guardian_photos/', null=True, blank=True, help_text="Photo")

    class Meta:
        db_table = 'guardian'
        verbose_name = 'Guardian'
        verbose_name_plural = 'Guardians'
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.relation})"

    def get_full_name(self):
        """Return the full name of the guardian."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class StudentGuardian(TimeStampedModel):
    """
    Links students to their guardians.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='guardians',
        help_text="Student reference"
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name='students',
        help_text="Guardian reference"
    )
    is_primary = models.BooleanField(default=False, help_text="Primary guardian")
    is_emergency_contact = models.BooleanField(default=False, help_text="Emergency contact")

    class Meta:
        db_table = 'student_guardian'
        verbose_name = 'Student Guardian'
        verbose_name_plural = 'Student Guardians'
        unique_together = ['student', 'guardian']
        indexes = [
            models.Index(fields=['student', 'guardian']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.guardian.get_full_name()}"


class StudentAddress(TimeStampedModel):
    """
    Stores student addresses (permanent, current, etc.).
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='addresses',
        help_text="Student reference"
    )
    address_type = models.CharField(
        max_length=20,
        help_text="Address type (permanent/current/hostel)"
    )
    address_line1 = models.CharField(max_length=255, help_text="Address line 1")
    address_line2 = models.CharField(max_length=255, null=True, blank=True, help_text="Address line 2")
    city = models.CharField(max_length=100, help_text="City")
    state = models.CharField(max_length=100, help_text="State")
    pincode = models.CharField(max_length=10, help_text="Pincode")
    country = models.CharField(max_length=100, default='India', help_text="Country")

    class Meta:
        db_table = 'student_address'
        verbose_name = 'Student Address'
        verbose_name_plural = 'Student Addresses'
        unique_together = ['student', 'address_type']
        indexes = [
            models.Index(fields=['student']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.address_type}"


class StudentDocument(AuditModel):
    """
    Stores student documents (certificates, ID proofs, etc.).
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="Student reference"
    )
    document_type = models.CharField(
        max_length=20,
        help_text="Document type (aadhar/pan/marksheet/certificate)"
    )
    document_name = models.CharField(max_length=200, help_text="Document name")
    document_file = models.FileField(upload_to='student_documents/', help_text="Document file")
    uploaded_date = models.DateField(auto_now_add=True, help_text="Upload date")
    is_verified = models.BooleanField(default=False, help_text="Verified status")
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_student_documents',
        help_text="Verified by"
    )
    verified_date = models.DateField(null=True, blank=True, help_text="Verification date")
    notes = models.TextField(null=True, blank=True, help_text="Notes")

    class Meta:
        db_table = 'student_document'
        verbose_name = 'Student Document'
        verbose_name_plural = 'Student Documents'
        indexes = [
            models.Index(fields=['student', 'document_type']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.document_name}"


class StudentMedicalRecord(AuditModel):
    """
    Stores student medical information.
    """
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='medical_record',
        help_text="Student reference"
    )
    blood_group = models.CharField(max_length=5, null=True, blank=True, help_text="Blood group")
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height in cm"
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kg"
    )
    allergies = models.TextField(null=True, blank=True, help_text="Allergies")
    medical_conditions = models.TextField(null=True, blank=True, help_text="Medical conditions")
    medications = models.TextField(null=True, blank=True, help_text="Current medications")
    emergency_contact_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Emergency contact"
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Emergency phone"
    )
    emergency_contact_relation = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Emergency relation"
    )
    health_insurance_provider = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Insurance provider"
    )
    health_insurance_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Insurance number"
    )
    last_checkup_date = models.DateField(null=True, blank=True, help_text="Last checkup")

    class Meta:
        db_table = 'student_medical_record'
        verbose_name = 'Student Medical Record'
        verbose_name_plural = 'Student Medical Records'
        indexes = [
            models.Index(fields=['student']),
        ]

    def __str__(self):
        return f"Medical Record - {self.student.get_full_name()}"


class PreviousAcademicRecord(AuditModel):
    """
    Stores student's previous academic records.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='previous_records',
        help_text="Student reference"
    )
    level = models.CharField(
        max_length=20,
        help_text="Education level (10th/12th/ug/pg)"
    )
    institution_name = models.CharField(max_length=300, help_text="Institution")
    board_university = models.CharField(max_length=200, help_text="Board/University")
    year_of_passing = models.IntegerField(help_text="Passing year")
    marks_obtained = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Marks obtained"
    )
    total_marks = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total marks"
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage"
    )
    grade = models.CharField(max_length=10, null=True, blank=True, help_text="Grade")
    certificate_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Certificate number"
    )

    class Meta:
        db_table = 'previous_academic_record'
        verbose_name = 'Previous Academic Record'
        verbose_name_plural = 'Previous Academic Records'
        indexes = [
            models.Index(fields=['student', 'year_of_passing']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.level} ({self.year_of_passing})"


class StudentPromotion(AuditModel):
    """
    Tracks student promotions from one class to another.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='promotions',
        help_text="Student reference"
    )
    from_class = models.ForeignKey(
        Class,
        on_delete=models.PROTECT,
        related_name='promoted_from',
        help_text="From class"
    )
    to_class = models.ForeignKey(
        Class,
        on_delete=models.PROTECT,
        related_name='promoted_to',
        help_text="To class"
    )
    from_section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promoted_from',
        help_text="From section"
    )
    to_section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promoted_to',
        help_text="To section"
    )
    promotion_date = models.DateField(help_text="Promotion date")
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='promotions',
        help_text="Academic year"
    )
    remarks = models.TextField(null=True, blank=True, help_text="Remarks")

    class Meta:
        db_table = 'student_promotion'
        verbose_name = 'Student Promotion'
        verbose_name_plural = 'Student Promotions'
        indexes = [
            models.Index(fields=['student', 'promotion_date']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.from_class} to {self.to_class}"


class Certificate(AuditModel):
    """
    Stores certificates issued to students.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='certificates',
        help_text="Student reference"
    )
    certificate_type = models.CharField(
        max_length=30,
        help_text="Certificate type (bonafide/tc/marksheet/degree)"
    )
    certificate_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Certificate number"
    )
    issue_date = models.DateField(help_text="Issue date")
    valid_until = models.DateField(null=True, blank=True, help_text="Valid until")
    purpose = models.TextField(null=True, blank=True, help_text="Purpose")
    certificate_file = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True,
        help_text="Certificate PDF"
    )
    signature_image = models.ImageField(
        upload_to='signatures/',
        null=True,
        blank=True,
        help_text="Signature"
    )
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_certificates',
        help_text="Signed by"
    )
    verification_code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Verification code"
    )

    class Meta:
        db_table = 'certificate'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        indexes = [
            models.Index(fields=['student', 'certificate_number']),
            models.Index(fields=['verification_code']),
        ]

    def __str__(self):
        return f"{self.certificate_type} - {self.student.get_full_name()} ({self.certificate_number})"


class StudentIDCard(AuditModel):
    """
    Stores student ID card information.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='id_cards',
        help_text="Student reference"
    )
    card_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Card number"
    )
    issue_date = models.DateField(help_text="Issue date")
    valid_until = models.DateField(help_text="Valid until")
    qr_code = models.ImageField(
        upload_to='id_qr_codes/',
        null=True,
        blank=True,
        help_text="QR code image"
    )
    card_file = models.FileField(
        upload_to='id_cards/',
        null=True,
        blank=True,
        help_text="Card PDF"
    )
    is_reissue = models.BooleanField(default=False, help_text="Reissue flag")
    reissue_reason = models.TextField(null=True, blank=True, help_text="Reissue reason")

    class Meta:
        db_table = 'student_id_card'
        verbose_name = 'Student ID Card'
        verbose_name_plural = 'Student ID Cards'
        indexes = [
            models.Index(fields=['student', 'card_number']),
        ]

    def __str__(self):
        return f"ID Card - {self.student.get_full_name()} ({self.card_number})"
