"""
DRF Serializers for HR app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    LeaveType,
    LeaveApplication,
    LeaveApproval,
    LeaveBalance,
    SalaryStructure,
    SalaryComponent,
    Deduction,
    Payroll,
    PayrollItem,
    Payslip,
)

User = get_user_model()


# ============================================================================
# BASE SERIALIZERS
# ============================================================================


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for nested representations."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields


class TenantAuditMixin(serializers.Serializer):
    """Mixin to include audit fields in serializers."""
    created_by = UserBasicSerializer(read_only=True)
    updated_by = UserBasicSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


# ============================================================================
# LEAVE TYPE SERIALIZERS
# ============================================================================


class LeaveTypeSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for LeaveType model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = LeaveType
        fields = [
            'id', 'college', 'college_name', 'name', 'code',
            'max_days_per_year', 'is_paid', 'description', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# LEAVE APPLICATION SERIALIZERS
# ============================================================================


class LeaveApplicationListSerializer(serializers.ModelSerializer):
    """Serializer for listing leave applications (minimal fields)."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'teacher', 'teacher_name', 'leave_type', 'leave_type_name',
            'from_date', 'to_date', 'total_days', 'status', 'applied_date'
        ]
        read_only_fields = ['id', 'teacher_name', 'leave_type_name', 'applied_date']


class LeaveApplicationSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """
    Full serializer for LeaveApplication.
    Automatically sets teacher from logged-in user if not provided.
    """
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveApplication
        fields = [
            'id', 'teacher', 'teacher_name', 'leave_type', 'leave_type_name',
            'from_date', 'to_date', 'total_days', 'reason', 'attachment',
            'status', 'applied_date',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name', 'leave_type_name', 'applied_date',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'teacher': {'required': False, 'allow_null': True}
        }

    def validate(self, data):
        """
        Auto-detect teacher based on user role:
        - If logged-in user is a teacher: auto-use their profile (ignore frontend value)
        - If logged-in user is admin/staff: allow them to specify teacher
        - Otherwise: raise error
        """
        request = self.context.get('request')

        if not request:
            raise serializers.ValidationError({
                'teacher': 'Request context is required.'
            })

        user = request.user

        # If logged-in user is a teacher, auto-use their teacher profile
        if hasattr(user, 'teacher_profile') and user.teacher_profile:
            data['teacher'] = user.teacher_profile
        # If user is admin/staff, they must specify a teacher
        elif (user.is_staff or user.is_superuser or
              user.user_type in ['college_admin', 'super_admin', 'staff']):
            if 'teacher' not in data or not data.get('teacher'):
                raise serializers.ValidationError({
                    'teacher': 'Admin must specify a teacher for the leave application.'
                })
            # Admin provided teacher - use it as is
        else:
            # User is neither teacher nor admin
            raise serializers.ValidationError({
                'teacher': 'Only teachers and admins can create leave applications.'
            })

        return data


# ============================================================================
# LEAVE APPROVAL SERIALIZERS
# ============================================================================


class LeaveApprovalSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for LeaveApproval model."""
    teacher_name = serializers.CharField(source='application.teacher.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='application.leave_type.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = LeaveApproval
        fields = [
            'id', 'application', 'teacher_name', 'leave_type_name',
            'status', 'approved_by', 'approved_by_name',
            'approval_date', 'remarks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name', 'leave_type_name', 'approved_by_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# LEAVE BALANCE SERIALIZERS
# ============================================================================


class LeaveBalanceSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for LeaveBalance model."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'teacher', 'teacher_name', 'leave_type', 'leave_type_name',
            'academic_year', 'academic_year_name', 'total_days', 'used_days', 'balance_days',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name', 'leave_type_name', 'academic_year_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# SALARY STRUCTURE SERIALIZERS
# ============================================================================


class SalaryStructureListSerializer(serializers.ModelSerializer):
    """Serializer for listing salary structures (minimal fields)."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = SalaryStructure
        fields = [
            'id', 'teacher', 'teacher_name', 'effective_from', 'effective_to',
            'basic_salary', 'gross_salary', 'is_current'
        ]
        read_only_fields = ['id', 'teacher_name']


class SalaryStructureSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for SalaryStructure model."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = SalaryStructure
        fields = [
            'id', 'teacher', 'teacher_name', 'effective_from', 'effective_to',
            'basic_salary', 'hra', 'da', 'other_allowances', 'gross_salary', 'is_current',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# SALARY COMPONENT SERIALIZERS
# ============================================================================


class SalaryComponentSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for SalaryComponent model."""
    teacher_name = serializers.CharField(source='structure.teacher.get_full_name', read_only=True)

    class Meta:
        model = SalaryComponent
        fields = [
            'id', 'structure', 'teacher_name', 'component_name', 'component_type',
            'amount', 'is_taxable',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# DEDUCTION SERIALIZERS
# ============================================================================


class DeductionSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for Deduction model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = Deduction
        fields = [
            'id', 'college', 'college_name', 'name', 'code',
            'deduction_type', 'amount', 'percentage', 'is_active',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'college_name', 'created_by', 'updated_by', 'created_at', 'updated_at']


# ============================================================================
# PAYROLL SERIALIZERS
# ============================================================================


class PayrollListSerializer(serializers.ModelSerializer):
    """Serializer for listing payrolls (minimal fields)."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = Payroll
        fields = [
            'id', 'teacher', 'teacher_name', 'month', 'year',
            'gross_salary', 'net_salary', 'payment_date', 'status'
        ]
        read_only_fields = ['id', 'teacher_name']


class PayrollSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Full serializer for Payroll model."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = Payroll
        fields = [
            'id', 'teacher', 'teacher_name', 'month', 'year',
            'salary_structure', 'gross_salary', 'total_allowances',
            'total_deductions', 'net_salary', 'payment_date',
            'payment_method', 'status', 'remarks',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# PAYROLL ITEM SERIALIZERS
# ============================================================================


class PayrollItemSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for PayrollItem model."""
    teacher_name = serializers.CharField(source='payroll.teacher.get_full_name', read_only=True)

    class Meta:
        model = PayrollItem
        fields = [
            'id', 'payroll', 'teacher_name', 'component_name',
            'component_type', 'amount',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


# ============================================================================
# PAYSLIP SERIALIZERS
# ============================================================================


class PayslipSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """Serializer for Payslip model."""
    teacher_name = serializers.CharField(source='payroll.teacher.get_full_name', read_only=True)

    class Meta:
        model = Payslip
        fields = [
            'id', 'payroll', 'teacher_name', 'slip_number',
            'slip_file', 'issue_date',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'teacher_name',
            'created_by', 'updated_by', 'created_at', 'updated_at'
        ]


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
