"""
URL configuration for Accounting app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IncomeCategoryViewSet,
    ExpenseCategoryViewSet,
    IncomeViewSet,
    ExpenseViewSet,
    AccountViewSet,
    VoucherViewSet,
    FinancialYearViewSet,
    AccountTransactionViewSet,
)

router = DefaultRouter()
router.register(r'income-categories', IncomeCategoryViewSet, basename='incomecategory')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expensecategory')
router.register(r'income', IncomeViewSet, basename='income')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'vouchers', VoucherViewSet, basename='voucher')
router.register(r'financial-years', FinancialYearViewSet, basename='financialyear')
router.register(r'account-transactions', AccountTransactionViewSet, basename='accounttransaction')

urlpatterns = [
    path('', include(router.urls)),
]
