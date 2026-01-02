from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedModelViewSet
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
from .serializers import (
    FeeGroupSerializer,
    FeeTypeSerializer,
    FeeMasterSerializer,
    FeeStructureSerializer,
    FeeDiscountSerializer,
    StudentFeeDiscountSerializer,
    FeeCollectionSerializer,
    FeeReceiptSerializer,
    FeeInstallmentSerializer,
    FeeFineSerializer,
    FeeRefundSerializer,
    BankPaymentSerializer,
    OnlinePaymentSerializer,
    FeeReminderSerializer,
)


class FeeGroupViewSet(CollegeScopedModelViewSet):
    queryset = FeeGroup.objects.all_colleges().select_related('college')
    serializer_class = FeeGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class FeeTypeViewSet(CollegeScopedModelViewSet):
    queryset = FeeType.objects.all_colleges().select_related('college', 'fee_group')
    serializer_class = FeeTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['fee_group', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class FeeMasterViewSet(CollegeScopedModelViewSet):
    queryset = FeeMaster.objects.all_colleges().select_related('college', 'program', 'academic_year', 'fee_type')
    serializer_class = FeeMasterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['program', 'academic_year', 'semester', 'fee_type', 'is_active']
    ordering_fields = ['semester', 'amount', 'created_at']
    ordering = ['semester']


class FeeDiscountViewSet(CollegeScopedModelViewSet):
    queryset = FeeDiscount.objects.all_colleges()
    serializer_class = FeeDiscountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['discount_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'fee_master', 'is_paid', 'is_active']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['due_date']


class StudentFeeDiscountViewSet(viewsets.ModelViewSet):
    queryset = StudentFeeDiscount.objects.all()
    serializer_class = StudentFeeDiscountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'discount', 'is_active']
    ordering_fields = ['applied_date', 'created_at']
    ordering = ['-applied_date']


class FeeCollectionViewSet(viewsets.ModelViewSet):
    queryset = FeeCollection.objects.all()
    serializer_class = FeeCollectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'status', 'payment_method', 'is_active']
    search_fields = ['transaction_id']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']


class FeeReceiptViewSet(viewsets.ModelViewSet):
    queryset = FeeReceipt.objects.all()
    serializer_class = FeeReceiptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['collection', 'is_active']
    search_fields = ['receipt_number']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class FeeInstallmentViewSet(viewsets.ModelViewSet):
    queryset = FeeInstallment.objects.all()
    serializer_class = FeeInstallmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'fee_structure', 'is_paid', 'is_active']
    ordering_fields = ['installment_number', 'due_date']
    ordering = ['installment_number']


class FeeFineViewSet(viewsets.ModelViewSet):
    queryset = FeeFine.objects.all()
    serializer_class = FeeFineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'fine_date', 'is_paid', 'is_active']
    ordering_fields = ['fine_date', 'created_at']
    ordering = ['-fine_date']


class FeeRefundViewSet(viewsets.ModelViewSet):
    queryset = FeeRefund.objects.all()
    serializer_class = FeeRefundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'refund_date', 'payment_method', 'is_active']
    ordering_fields = ['refund_date', 'amount']
    ordering = ['-refund_date']


class BankPaymentViewSet(viewsets.ModelViewSet):
    queryset = BankPayment.objects.all()
    serializer_class = BankPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['collection', 'is_active']
    search_fields = ['cheque_dd_number', 'transaction_id', 'bank_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class OnlinePaymentViewSet(viewsets.ModelViewSet):
    queryset = OnlinePayment.objects.all()
    serializer_class = OnlinePaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['collection', 'gateway', 'status', 'is_active']
    search_fields = ['transaction_id', 'order_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class FeeReminderViewSet(viewsets.ModelViewSet):
    queryset = FeeReminder.objects.all()
    serializer_class = FeeReminderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'fee_structure', 'status', 'is_active']
    ordering_fields = ['reminder_date', 'created_at']
    ordering = ['-reminder_date']
