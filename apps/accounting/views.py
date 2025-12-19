from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedModelViewSet
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
from .serializers import (
    IncomeCategorySerializer,
    ExpenseCategorySerializer,
    IncomeSerializer,
    ExpenseSerializer,
    AccountSerializer,
    VoucherSerializer,
    FinancialYearSerializer,
    AccountTransactionSerializer,
)


class IncomeCategoryViewSet(CollegeScopedModelViewSet):
    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class ExpenseCategoryViewSet(CollegeScopedModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class AccountViewSet(CollegeScopedModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'bank_name']
    search_fields = ['account_name', 'account_number', 'bank_name']
    ordering_fields = ['account_name', 'created_at']
    ordering = ['account_name']


class FinancialYearViewSet(CollegeScopedModelViewSet):
    queryset = FinancialYear.objects.all()
    serializer_class = FinancialYearSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_current', 'is_active']
    ordering_fields = ['start_date', 'year']
    ordering = ['-start_date']


class IncomeViewSet(CollegeScopedModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'date', 'payment_method', 'is_active']
    search_fields = ['description', 'invoice_number']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']


class ExpenseViewSet(CollegeScopedModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'date', 'payment_method', 'is_active']
    search_fields = ['description', 'receipt_number', 'paid_to']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']


class VoucherViewSet(CollegeScopedModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['voucher_type', 'date', 'is_active']
    search_fields = ['voucher_number', 'description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']


class AccountTransactionViewSet(viewsets.ModelViewSet):
    queryset = AccountTransaction.objects.all()
    serializer_class = AccountTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account', 'transaction_type', 'date', 'is_active']
    search_fields = ['description', 'reference_type']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
