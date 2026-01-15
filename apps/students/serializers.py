"""
DRF Serializers for Students app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    StudentCategory, StudentGroup, Student, Guardian, StudentGuardian,
    StudentAddress, StudentDocument, StudentMedicalRecord, PreviousAcademicRecord,
    StudentPromotion, Certificate, StudentIDCard
)
from apps.core.serializers import UserBasicSerializer, TenantAuditMixin

User = get_user_model()


# ============================================================================
# STUDENT CATEGORY SERIALIZERS
# ============================================================================


class StudentCategorySerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for StudentCategory model."""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = StudentCategory
        fields = [
            'id', 'college', 'college_name', 'name', 'code', 'description', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# STUDENT GROUP SERIALIZERS
# ============================================================================


class StudentGroupSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for StudentGroup model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = StudentGroup
        fields = [
            'id', 'college', 'college_name', 'name', 'description', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# STUDENT SERIALIZERS
# ============================================================================


class StudentListSerializer(serializers.ModelSerializer):
    """Serializer for listing students (minimal fields)."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    program_name = serializers.CharField(source='program.short_name', read_only=True)
    current_class_name = serializers.CharField(source='current_class.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'registration_number', 'full_name',
            'email', 'phone', 'college', 'college_name', 'program', 'program_name',
            'current_class', 'current_class_name', 'is_active', 'is_alumni'
        ]
        read_only_fields = ['id', 'full_name', 'college_name', 'program_name', 'current_class_name']


class StudentSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Student model."""
    college_name = serializers.CharField(source='college.name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    current_class_name = serializers.CharField(source='current_class.name', read_only=True)
    current_section_name = serializers.CharField(source='current_section.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_details = UserBasicSerializer(source='user', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'user_details', 'college', 'college_name',
            'admission_number', 'admission_date', 'admission_type', 'roll_number',
            'registration_number', 'program', 'program_name',
            'current_class', 'current_class_name', 'current_section', 'current_section_name',
            'academic_year', 'academic_year_name', 'category', 'category_name', 'group', 'group_name',
            'first_name', 'middle_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'blood_group', 'email', 'phone', 'alternate_phone',
            'photo', 'nationality', 'religion', 'caste', 'mother_tongue',
            'aadhar_number', 'pan_number', 'is_active', 'is_alumni',
            'disabled_date', 'disable_reason', 'optional_subjects', 'custom_fields',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'college_name', 'program_name', 'current_class_name',
            'current_section_name', 'academic_year_name', 'category_name', 'group_name', 'user_details',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user': {
                'validators': []  # Disable uniqueness validation on updates
            }
        }


# ============================================================================
# GUARDIAN SERIALIZERS
# ============================================================================


class GuardianSerializer(serializers.ModelSerializer):
    """Serializer for Guardian model."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_details = UserBasicSerializer(source='user', read_only=True)

    class Meta:
        model = Guardian
        fields = [
            'id', 'user', 'user_details', 'first_name', 'middle_name', 'last_name',
            'full_name', 'relation', 'email', 'phone', 'alternate_phone',
            'occupation', 'annual_income', 'address', 'photo',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'user_details', 'created_at', 'updated_at']


# ============================================================================
# STUDENT GUARDIAN SERIALIZERS
# ============================================================================


class StudentGuardianSerializer(serializers.ModelSerializer):
    """Serializer for StudentGuardian model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    guardian_details = GuardianSerializer(source='guardian', read_only=True)

    class Meta:
        model = StudentGuardian
        fields = [
            'id', 'student', 'student_name', 'guardian', 'guardian_details',
            'is_primary', 'is_emergency_contact',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'guardian_details', 'created_at', 'updated_at']


# ============================================================================
# STUDENT ADDRESS SERIALIZERS
# ============================================================================


class StudentAddressSerializer(serializers.ModelSerializer):
    """Serializer for StudentAddress model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = StudentAddress
        fields = [
            'id', 'student', 'student_name', 'address_type',
            'address_line1', 'address_line2', 'city', 'state', 'pincode', 'country',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'created_at', 'updated_at']


# ============================================================================
# STUDENT DOCUMENT SERIALIZERS
# ============================================================================


class StudentDocumentSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for StudentDocument model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    verified_by_details = UserBasicSerializer(source='verified_by', read_only=True)

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student', 'student_name', 'document_type', 'document_name',
            'document_file', 'uploaded_date', 'is_verified', 'verified_by',
            'verified_by_details', 'verified_date', 'notes', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'uploaded_date', 'verified_by_details',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# STUDENT MEDICAL RECORD SERIALIZERS
# ============================================================================


class StudentMedicalRecordSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for StudentMedicalRecord model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = StudentMedicalRecord
        fields = [
            'id', 'student', 'student_name', 'blood_group', 'height', 'weight',
            'allergies', 'medical_conditions', 'medications',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'health_insurance_provider', 'health_insurance_number', 'last_checkup_date',
            'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# PREVIOUS ACADEMIC RECORD SERIALIZERS
# ============================================================================


class PreviousAcademicRecordSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for PreviousAcademicRecord model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = PreviousAcademicRecord
        fields = [
            'id', 'student', 'student_name', 'level', 'institution_name',
            'board_university', 'year_of_passing', 'marks_obtained', 'total_marks',
            'percentage', 'grade', 'certificate_number', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# STUDENT PROMOTION SERIALIZERS
# ============================================================================


class StudentPromotionSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for StudentPromotion model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    from_class_name = serializers.CharField(source='from_class.name', read_only=True)
    to_class_name = serializers.CharField(source='to_class.name', read_only=True)
    from_section_name = serializers.CharField(source='from_section.name', read_only=True)
    to_section_name = serializers.CharField(source='to_section.name', read_only=True)

    class Meta:
        model = StudentPromotion
        fields = [
            'id', 'student', 'student_name',
            'from_class', 'from_class_name', 'to_class', 'to_class_name',
            'from_section', 'from_section_name', 'to_section', 'to_section_name',
            'promotion_date', 'academic_year', 'remarks', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'from_class_name', 'to_class_name',
            'from_section_name', 'to_section_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# CERTIFICATE SERIALIZERS
# ============================================================================


class CertificateSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for Certificate model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    signed_by_details = UserBasicSerializer(source='signed_by', read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'student', 'student_name', 'certificate_type', 'certificate_number',
            'issue_date', 'valid_until', 'purpose', 'certificate_file',
            'signature_image', 'signed_by', 'signed_by_details', 'verification_code',
            'is_active', 'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'student_name', 'verification_code', 'signed_by_details',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# STUDENT ID CARD SERIALIZERS
# ============================================================================


class StudentIDCardSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for StudentIDCard model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = StudentIDCard
        fields = [
            'id', 'student', 'student_name', 'card_number', 'issue_date', 'valid_until',
            'qr_code', 'card_file', 'is_active', 'is_reissue', 'reissue_reason',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'student_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


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
