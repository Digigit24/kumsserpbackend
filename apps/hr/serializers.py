from rest_framework import serializers

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


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for LeaveApplication.
    Automatically sets teacher from logged-in user if not provided.
    """

    class Meta:
        model = LeaveApplication
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by']
        extra_kwargs = {
            'teacher': {'required': False, 'allow_null': True}
        }

    def validate(self, data):
        """ALWAYS use logged-in user's teacher profile, ignore whatever is sent."""
        request = self.context.get('request')

        # ALWAYS override teacher with logged-in user (ignore frontend value)
        if request and hasattr(request.user, 'teacher_profile') and request.user.teacher_profile:
            data['teacher'] = request.user.teacher_profile
        else:
            raise serializers.ValidationError({
                'teacher': 'Current user does not have a teacher profile.'
            })

        return data


class LeaveApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApproval
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__'


class SalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = '__all__'


class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = '__all__'


class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = '__all__'


class PayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = '__all__'


class PayrollItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollItem
        fields = '__all__'


class PayslipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = '__all__'
