from django.contrib import admin

from .models import (
    IncomeCategory,
    ExpenseCategory,
    Income,
    Expense,
    Account,
    Voucher,
    FinancialYear,
    AccountTransaction,
)


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active', 'college')


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'college', 'is_active')
    search_fields = ('name', 'code')
    list_filter = ('is_active', 'college')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'account_number', 'bank_name', 'college', 'balance', 'is_active')
    search_fields = ('account_name', 'account_number', 'bank_name')
    list_filter = ('is_active', 'college', 'bank_name')


@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'college', 'start_date', 'end_date', 'is_current', 'is_active')
    list_filter = ('is_active', 'is_current', 'college')


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'category', 'college', 'payment_method', 'is_active')
    list_filter = ('is_active', 'college', 'category', 'payment_method', 'date')
    search_fields = ('description', 'invoice_number')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'category', 'college', 'payment_method', 'is_active')
    list_filter = ('is_active', 'college', 'category', 'payment_method', 'date')
    search_fields = ('description', 'receipt_number', 'paid_to')


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher_number', 'voucher_type', 'amount', 'date', 'college', 'is_active')
    search_fields = ('voucher_number', 'description')
    list_filter = ('is_active', 'voucher_type', 'college')


@admin.register(AccountTransaction)
class AccountTransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'date', 'balance_after', 'is_active')
    list_filter = ('transaction_type', 'is_active', 'date')
    search_fields = ('description', 'reference_type')
