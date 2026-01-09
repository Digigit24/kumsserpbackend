from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.cache_mixins import CachedReadOnlyMixin

from apps.core.mixins import (
    CollegeScopedMixin, CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet
)
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
from .serializers import (
    LeaveTypeSerializer,
    LeaveApplicationSerializer,
    LeaveApprovalSerializer,
    LeaveBalanceSerializer,
    SalaryStructureSerializer,
    SalaryComponentSerializer,
    DeductionSerializer,
    PayrollSerializer,
    PayrollItemSerializer,
    PayslipSerializer,
)


class LeaveTypeViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    queryset = LeaveType.objects.all_colleges()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'max_days_per_year', 'created_at']
    ordering = ['name']


class LeaveApplicationViewSet(RelatedCollegeScopedModelViewSet):
    queryset = LeaveApplication.objects.select_related('teacher', 'leave_type')
    serializer_class = LeaveApplicationSerializer
    related_college_lookup = 'teacher__college_id'
    filterset_fields = ['teacher', 'leave_type', 'status', 'from_date', 'to_date', 'is_active']
    ordering_fields = ['from_date', 'to_date', 'created_at']
    ordering = ['-from_date']


class LeaveApprovalViewSet(RelatedCollegeScopedModelViewSet):
    queryset = LeaveApproval.objects.select_related('application', 'application__teacher')
    serializer_class = LeaveApprovalSerializer
    related_college_lookup = 'application__teacher__college_id'
    filterset_fields = ['status', 'approved_by', 'approval_date', 'application', 'is_active']
    ordering_fields = ['approval_date', 'created_at']
    ordering = ['-approval_date']


class LeaveBalanceViewSet(RelatedCollegeScopedModelViewSet):
    queryset = LeaveBalance.objects.select_related('teacher', 'leave_type', 'academic_year')
    serializer_class = LeaveBalanceSerializer
    related_college_lookup = 'teacher__college_id'
    filterset_fields = ['teacher', 'leave_type', 'academic_year', 'is_active']
    ordering_fields = ['balance_days', 'used_days', 'created_at']
    ordering = ['-balance_days']


class SalaryStructureViewSet(RelatedCollegeScopedModelViewSet):
    queryset = SalaryStructure.objects.select_related('teacher')
    serializer_class = SalaryStructureSerializer
    related_college_lookup = 'teacher__college_id'
    filterset_fields = ['teacher', 'is_current', 'effective_from', 'effective_to', 'is_active']
    ordering_fields = ['effective_from', 'effective_to', 'created_at']
    ordering = ['-effective_from']


class SalaryComponentViewSet(RelatedCollegeScopedModelViewSet):
    queryset = SalaryComponent.objects.select_related('structure', 'structure__teacher')
    serializer_class = SalaryComponentSerializer
    related_college_lookup = 'structure__teacher__college_id'
    filterset_fields = ['structure', 'component_type', 'is_active']
    ordering_fields = ['amount', 'created_at']
    ordering = ['component_name']


class DeductionViewSet(CachedReadOnlyMixin, CollegeScopedModelViewSet):
    queryset = Deduction.objects.all_colleges()
    serializer_class = DeductionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['deduction_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'amount', 'percentage', 'created_at']
    ordering = ['name']


class PayrollViewSet(RelatedCollegeScopedModelViewSet):
    queryset = Payroll.objects.select_related('teacher', 'salary_structure')
    serializer_class = PayrollSerializer
    related_college_lookup = 'teacher__college_id'
    filterset_fields = ['teacher', 'month', 'year', 'status', 'payment_date', 'is_active']
    ordering_fields = ['year', 'month', 'net_salary', 'created_at']
    ordering = ['-year', '-month']


class PayrollItemViewSet(RelatedCollegeScopedModelViewSet):
    queryset = PayrollItem.objects.select_related('payroll', 'payroll__teacher')
    serializer_class = PayrollItemSerializer
    related_college_lookup = 'payroll__teacher__college_id'
    filterset_fields = ['payroll', 'component_type', 'is_active']
    ordering_fields = ['amount', 'created_at']
    ordering = ['component_name']


class PayslipViewSet(RelatedCollegeScopedModelViewSet):
    queryset = Payslip.objects.select_related('payroll', 'payroll__teacher')
    serializer_class = PayslipSerializer
    related_college_lookup = 'payroll__teacher__college_id'
    filterset_fields = ['payroll', 'issue_date', 'is_active']
    ordering_fields = ['issue_date', 'created_at']
    ordering = ['-issue_date']
