from rest_framework import serializers

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


class FeeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeGroup
        fields = '__all__'


class FeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeType
        fields = '__all__'


class FeeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeMaster
        fields = '__all__'


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


class StudentFeeDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeDiscount
        fields = '__all__'


class FeeCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCollection
        fields = '__all__'


class FeeReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeReceipt
        fields = '__all__'


class FeeInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeInstallment
        fields = '__all__'


class FeeFineSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeFine
        fields = '__all__'


class FeeRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeRefund
        fields = '__all__'


class BankPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankPayment
        fields = '__all__'


class OnlinePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlinePayment
        fields = '__all__'


class FeeReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeReminder
        fields = '__all__'
