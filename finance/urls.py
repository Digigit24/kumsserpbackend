from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AppIncomeViewSet,
    AppExpenseViewSet,
    AppTotalViewSet,
    FinanceTotalViewSet,
    OtherExpenseViewSet,
    FinanceTransactionViewSet,
    FinanceReportViewSet
)

router = DefaultRouter()
router.register(r'app-income', AppIncomeViewSet, basename='app-income')
router.register(r'app-expense', AppExpenseViewSet, basename='app-expense')
router.register(r'app-total', AppTotalViewSet, basename='app-total')
router.register(r'finance-total', FinanceTotalViewSet, basename='finance-total')
router.register(r'other-expenses', OtherExpenseViewSet, basename='other-expenses')
router.register(r'transactions', FinanceTransactionViewSet, basename='transactions')
router.register(r'reports', FinanceReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
