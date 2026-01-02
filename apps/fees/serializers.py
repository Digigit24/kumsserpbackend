"""
DRF Serializers for Fees app models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    FeeGroup,
    FeeType,
    FeeMaster,
    FeeStructure,
    FeeDiscount,
    StudentFeeDiscount,
    FeeCollection,
    FeeReceipt,
    FeeInstallment,
    FeeFine,
    FeeRefund,
    BankPayment,
    OnlinePayment,
    FeeReminder,
)
from apps.students.models import Student

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


# ============================================================================
# FEE GROUP SERIALIZERS
# ============================================================================


class FeeGroupSerializer(serializers.ModelSerializer):
    """Serializer for FeeGroup model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)

    class Meta:
        model = FeeGroup
        fields = ['id', 'college', 'college_name', 'name', 'code', 'description', 'is_active']
        read_only_fields = ['id', 'college_name']


# ============================================================================
# FEE TYPE SERIALIZERS
# ============================================================================


class FeeTypeSerializer(serializers.ModelSerializer):
    """Serializer for FeeType model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    fee_group_name = serializers.CharField(source='fee_group.name', read_only=True)

    class Meta:
        model = FeeType
        fields = [
            'id', 'college', 'college_name', 'fee_group', 'fee_group_name',
            'name', 'code', 'description', 'is_active'
        ]
        read_only_fields = ['id', 'college_name', 'fee_group_name']


# ============================================================================
# FEE MASTER SERIALIZERS
# ============================================================================


class FeeMasterSerializer(serializers.ModelSerializer):
    """Serializer for FeeMaster model."""
    college_name = serializers.CharField(source='college.short_name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.year', read_only=True)
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)

    class Meta:
        model = FeeMaster
        fields = [
            'id', 'college', 'college_name', 'program', 'program_name',
            'academic_year', 'academic_year_name', 'class_obj', 'semester',
            'fee_type', 'fee_type_name', 'amount', 'due_date', 'is_active'
        ]
        read_only_fields = ['id', 'college_name', 'program_name', 'academic_year_name', 'fee_type_name']


# Nested serializers for read-only display
class StudentDisplaySerializer(serializers.ModelSerializer):
    """Serializer for displaying student name in fee structures"""
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'admission_number', 'student_name', 'first_name', 'last_name']

    def get_student_name(self, obj):
        return obj.get_full_name()


class FeeMasterDisplaySerializer(serializers.ModelSerializer):
    """Serializer for displaying fee master details in fee structures"""
    program_name = serializers.CharField(source='program.name', read_only=True)
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)

    class Meta:
        model = FeeMaster
        fields = ['id', 'program_name', 'semester', 'fee_type_name', 'amount']


class FeeStructureSerializer(serializers.ModelSerializer):
    # Use nested serializers for read operations
    student_details = StudentDisplaySerializer(source='student', read_only=True)
    fee_master_details = FeeMasterDisplaySerializer(source='fee_master', read_only=True)

    class Meta:
        model = FeeStructure
        fields = '__all__'

    def to_representation(self, instance):
        """Override to include nested details in response"""
        representation = super().to_representation(instance)
        # Add student_name at the top level for easier access
        if instance.student:
            representation['student_name'] = instance.student.get_full_name()
        return representation


class FeeDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeDiscount
        fields = '__all__'


class FeeDiscountDisplaySerializer(serializers.ModelSerializer):
    """Serializer for displaying discount details"""
    class Meta:
        model = FeeDiscount
        fields = ['id', 'name', 'code', 'discount_type', 'amount', 'percentage']


class StudentFeeDiscountSerializer(serializers.ModelSerializer):
    # Use nested serializers for read operations
    student_details = StudentDisplaySerializer(source='student', read_only=True)
    discount_details = FeeDiscountDisplaySerializer(source='discount', read_only=True)

    class Meta:
        model = StudentFeeDiscount
        fields = '__all__'

    def to_representation(self, instance):
        """Override to include nested details in response"""
        representation = super().to_representation(instance)
        # Add student_name at the top level for easier access
        if instance.student:
            representation['student_name'] = instance.student.get_full_name()
        if instance.discount:
            representation['discount_name'] = instance.discount.name
        return representation


class FeeCollectionSerializer(serializers.ModelSerializer):
    """Serializer for FeeCollection model."""
    student_details = StudentDisplaySerializer(source='student', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    collected_by_name = serializers.CharField(source='collected_by.get_full_name', read_only=True)

    class Meta:
        model = FeeCollection
        fields = '__all__'


class FeeReceiptSerializer(serializers.ModelSerializer):
    """Serializer for FeeReceipt model."""
    student_name = serializers.CharField(source='collection.student.get_full_name', read_only=True)

    class Meta:
        model = FeeReceipt
        fields = '__all__'


class FeeInstallmentSerializer(serializers.ModelSerializer):
    # Use nested serializers for read operations
    student_details = StudentDisplaySerializer(source='student', read_only=True)
    fee_structure_details = serializers.SerializerMethodField()

    class Meta:
        model = FeeInstallment
        fields = '__all__'

    def get_fee_structure_details(self, obj):
        if obj.fee_structure:
            return {
                'id': obj.fee_structure.id,
                'amount': str(obj.fee_structure.amount),
                'due_date': obj.fee_structure.due_date
            }
        return None

    def to_representation(self, instance):
        """Override to include nested details in response"""
        representation = super().to_representation(instance)
        # Add student_name at the top level for easier access
        if instance.student:
            representation['student_name'] = instance.student.get_full_name()
        return representation


class FeeFineSerializer(serializers.ModelSerializer):
    # Use nested serializers for read operations
    student_details = StudentDisplaySerializer(source='student', read_only=True)

    class Meta:
        model = FeeFine
        fields = '__all__'

    def to_representation(self, instance):
        """Override to include nested details in response"""
        representation = super().to_representation(instance)
        # Add student_name at the top level for easier access
        if instance.student:
            representation['student_name'] = instance.student.get_full_name()
        return representation


class FeeRefundSerializer(serializers.ModelSerializer):
    # Use nested serializers for read operations
    student_details = StudentDisplaySerializer(source='student', read_only=True)

    class Meta:
        model = FeeRefund
        fields = '__all__'

    def to_representation(self, instance):
        """Override to include nested details in response"""
        representation = super().to_representation(instance)
        # Add student_name at the top level for easier access
        if instance.student:
            representation['student_name'] = instance.student.get_full_name()
        return representation


class BankPaymentSerializer(serializers.ModelSerializer):
    """Serializer for BankPayment model."""
    student_name = serializers.CharField(source='collection.student.get_full_name', read_only=True)

    class Meta:
        model = BankPayment
        fields = '__all__'


class OnlinePaymentSerializer(serializers.ModelSerializer):
    """Serializer for OnlinePayment model."""
    student_name = serializers.CharField(source='collection.student.get_full_name', read_only=True)

    class Meta:
        model = OnlinePayment
        fields = '__all__'


class FeeReminderSerializer(serializers.ModelSerializer):
    # Use nested serializers for read operations
    student_details = StudentDisplaySerializer(source='student', read_only=True)
    fee_structure_details = serializers.SerializerMethodField()

    class Meta:
        model = FeeReminder
        fields = '__all__'

    def get_fee_structure_details(self, obj):
        if obj.fee_structure:
            return {
                'id': obj.fee_structure.id,
                'amount': str(obj.fee_structure.amount),
                'due_date': obj.fee_structure.due_date,
                'balance': str(obj.fee_structure.balance)
            }
        return None

    def to_representation(self, instance):
        """Override to include nested details in response"""
        representation = super().to_representation(instance)
        # Add student_name at the top level for easier access
        if instance.student:
            representation['student_name'] = instance.student.get_full_name()
        return representation
