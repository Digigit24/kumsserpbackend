from django.contrib import admin

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


@admin.register(FeeGroup)
class FeeGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active', 'college')


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'fee_group', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active', 'college', 'fee_group')


@admin.register(FeeMaster)
class FeeMasterAdmin(admin.ModelAdmin):
    list_display = ('program', 'academic_year', 'semester', 'fee_type', 'amount', 'is_active')
    list_filter = ('college', 'program', 'academic_year', 'semester', 'fee_type', 'is_active')


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_master', 'amount', 'due_date', 'is_paid', 'balance', 'is_active')
    list_filter = ('is_paid', 'is_active', 'due_date', 'fee_master')
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(FeeDiscount)
class FeeDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'discount_type', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('discount_type', 'is_active', 'college')


@admin.register(StudentFeeDiscount)
class StudentFeeDiscountAdmin(admin.ModelAdmin):
    list_display = ('student', 'discount', 'applied_date', 'is_active')
    list_filter = ('discount', 'is_active')


@admin.register(FeeCollection)
class FeeCollectionAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'payment_method', 'payment_date', 'status', 'is_active')
    list_filter = ('status', 'payment_method', 'is_active', 'payment_date')
    search_fields = ('transaction_id',)


@admin.register(FeeReceipt)
class FeeReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'collection', 'is_active')
    search_fields = ('receipt_number',)
    list_filter = ('is_active',)


@admin.register(FeeInstallment)
class FeeInstallmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'installment_number', 'amount', 'due_date', 'is_paid', 'is_active')
    list_filter = ('is_paid', 'is_active', 'due_date')


@admin.register(FeeFine)
class FeeFineAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount', 'fine_date', 'is_paid', 'is_active')
    list_filter = ('is_paid', 'is_active', 'fine_date')


@admin.register(FeeRefund)
class FeeRefundAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'refund_date', 'payment_method', 'is_active')
    list_filter = ('payment_method', 'is_active', 'refund_date')


@admin.register(BankPayment)
class BankPaymentAdmin(admin.ModelAdmin):
    list_display = ('collection', 'bank_name', 'transaction_id', 'is_active')
    search_fields = ('transaction_id', 'bank_name')
    list_filter = ('is_active',)


@admin.register(OnlinePayment)
class OnlinePaymentAdmin(admin.ModelAdmin):
    list_display = ('collection', 'gateway', 'transaction_id', 'status', 'is_active')
    search_fields = ('transaction_id', 'order_id')
    list_filter = ('gateway', 'status', 'is_active')


@admin.register(FeeReminder)
class FeeReminderAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'reminder_date', 'status', 'is_active')
    list_filter = ('status', 'is_active', 'reminder_date')
