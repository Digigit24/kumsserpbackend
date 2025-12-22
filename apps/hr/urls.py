"""
URL configuration for HR app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LeaveTypeViewSet,
    LeaveApplicationViewSet,
    LeaveApprovalViewSet,
    LeaveBalanceViewSet,
    SalaryStructureViewSet,
    SalaryComponentViewSet,
    DeductionViewSet,
    PayrollViewSet,
    PayrollItemViewSet,
    PayslipViewSet,
)

router = DefaultRouter()
router.register(r'leave-types', LeaveTypeViewSet, basename='leavetype')
router.register(r'leave-applications', LeaveApplicationViewSet, basename='leaveapplication')
router.register(r'leave-approvals', LeaveApprovalViewSet, basename='leaveapproval')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leavebalance')
router.register(r'salary-structures', SalaryStructureViewSet, basename='salarystructure')
router.register(r'salary-components', SalaryComponentViewSet, basename='salarycomponent')
router.register(r'deductions', DeductionViewSet, basename='deduction')
router.register(r'payrolls', PayrollViewSet, basename='payroll')
router.register(r'payroll-items', PayrollItemViewSet, basename='payrollitem')
router.register(r'payslips', PayslipViewSet, basename='payslip')

urlpatterns = [
    path('', include(router.urls)),
]
