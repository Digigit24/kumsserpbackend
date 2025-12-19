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


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'


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
