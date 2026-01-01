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
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        required=False,  # Make teacher optional
        allow_null=True,
        help_text="Teacher (auto-filled from logged-in user if not provided)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for teacher field
        from apps.teachers.models import Teacher
        self.fields['teacher'].queryset = Teacher.objects.all()

    class Meta:
        model = LeaveApplication
        fields = '__all__'
        read_only_fields = ['created_by', 'updated_by']

    def validate(self, data):
        """Auto-fill teacher from request user if not provided."""
        request = self.context.get('request')

        # If teacher not provided, try to get from logged-in user
        if 'teacher' not in data or data['teacher'] is None:
            if request and hasattr(request.user, 'teacher_profile'):
                data['teacher'] = request.user.teacher_profile
            else:
                raise serializers.ValidationError({
                    'teacher': 'Teacher is required. Current user does not have a teacher profile.'
                })

        return data

    def validate_teacher(self, value):
        """Validate that teacher exists."""
        if value is None:
            request = self.context.get('request')
            if request and hasattr(request.user, 'teacher_profile'):
                return request.user.teacher_profile
            raise serializers.ValidationError('Teacher is required.')
        return value


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
