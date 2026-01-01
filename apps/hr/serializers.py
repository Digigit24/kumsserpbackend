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
