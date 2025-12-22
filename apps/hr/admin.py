from django.contrib import admin

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


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'max_days_per_year', 'is_paid', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('college', 'is_paid', 'is_active')


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'leave_type', 'from_date', 'to_date', 'total_days', 'status', 'is_active')
    list_filter = ('status', 'from_date', 'to_date', 'is_active')
    search_fields = ('teacher__user__first_name', 'teacher__user__last_name')


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('application', 'status', 'approved_by', 'approval_date', 'is_active')
    list_filter = ('status', 'approval_date', 'is_active')


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'leave_type', 'academic_year', 'total_days', 'used_days', 'balance_days', 'is_active')
    list_filter = ('leave_type', 'academic_year', 'is_active')


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'effective_from', 'effective_to', 'gross_salary', 'is_current', 'is_active')
    list_filter = ('is_current', 'effective_from', 'is_active')


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ('structure', 'component_name', 'component_type', 'amount', 'is_active')
    list_filter = ('component_type', 'is_active')


@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'deduction_type', 'amount', 'percentage', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('college', 'deduction_type', 'is_active')


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'month', 'year', 'net_salary', 'status', 'payment_date', 'is_active')
    list_filter = ('status', 'month', 'year', 'is_active')


@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):
    list_display = ('payroll', 'component_name', 'component_type', 'amount', 'is_active')
    list_filter = ('component_type', 'is_active')


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('payroll', 'slip_number', 'issue_date', 'is_active')
    search_fields = ('slip_number',)
    list_filter = ('issue_date', 'is_active')
