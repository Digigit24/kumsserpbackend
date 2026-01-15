from django.contrib import admin
from .models import (
    AppIncome,
    AppExpense,
    AppTotal,
    FinanceTotal,
    OtherExpense,
    FinanceTransaction
)


@admin.register(AppIncome)
class AppIncomeAdmin(admin.ModelAdmin):
    list_display = ['app_name', 'month', 'amount', 'transaction_count', 'last_synced']
    list_filter = ['app_name', 'month']
    search_fields = ['app_name']
    ordering = ['-month', 'app_name']


@admin.register(AppExpense)
class AppExpenseAdmin(admin.ModelAdmin):
    list_display = ['app_name', 'month', 'amount', 'transaction_count', 'last_synced']
    list_filter = ['app_name', 'month']
    search_fields = ['app_name']
    ordering = ['-month', 'app_name']


@admin.register(AppTotal)
class AppTotalAdmin(admin.ModelAdmin):
    list_display = ['app_name', 'month', 'income', 'expense', 'net_total', 'last_updated']
    list_filter = ['app_name', 'month']
    search_fields = ['app_name']
    ordering = ['-month', 'app_name']


@admin.register(FinanceTotal)
class FinanceTotalAdmin(admin.ModelAdmin):
    list_display = ['month', 'total_income', 'total_expense', 'net_total', 'last_updated']
    list_filter = ['month']
    ordering = ['-month']


@admin.register(OtherExpense)
class OtherExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'category', 'date', 'created_by', 'created_at']
    list_filter = ['category', 'date', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_by', 'created_at', 'updated_at']


@admin.register(FinanceTransaction)
class FinanceTransactionAdmin(admin.ModelAdmin):
    list_display = ['app', 'type', 'amount', 'description', 'date', 'created_at']
    list_filter = ['app', 'type', 'date']
    search_fields = ['description', 'reference_model']
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at']
