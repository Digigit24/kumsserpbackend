from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.mixins import CollegeScopedMixin, CollegeScopedModelViewSet
from .models import (
    StoreCategory,
    StoreItem,
    Vendor,
    StockReceive,
    StoreSale,
    SaleItem,
    PrintJob,
    StoreCredit,
)
from .serializers import (
    StoreCategorySerializer,
    StoreItemSerializer,
    VendorSerializer,
    StockReceiveSerializer,
    StoreSaleSerializer,
    SaleItemSerializer,
    PrintJobSerializer,
    StoreCreditSerializer,
)


class RelatedCollegeScopedModelViewSet(CollegeScopedMixin, viewsets.ModelViewSet):
    """
    Scopes by college via a related lookup path when model lacks direct college FK.
    """
    related_college_lookup = None
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        college_id = self.get_college_id(required=False)
        user = getattr(self.request, 'user', None)

        if college_id == 'all' or (user and (user.is_superuser or user.is_staff) and not college_id):
            return queryset

        if not college_id:
            college_id = self.get_college_id(required=True)

        if not self.related_college_lookup:
            return queryset.none()

        return queryset.filter(**{self.related_college_lookup: college_id})


class StoreCategoryViewSet(CollegeScopedModelViewSet):
    queryset = StoreCategory.objects.all_colleges()
    serializer_class = StoreCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class StoreItemViewSet(CollegeScopedModelViewSet):
    queryset = StoreItem.objects.select_related('category', 'college').all_colleges()
    serializer_class = StoreItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'code', 'barcode']
    ordering_fields = ['name', 'stock_quantity', 'min_stock_level', 'price', 'created_at']
    ordering = ['name']


class VendorViewSet(CollegeScopedModelViewSet):
    queryset = Vendor.objects.select_related('college').all_colleges()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'phone', 'email', 'gstin']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class StockReceiveViewSet(RelatedCollegeScopedModelViewSet):
    queryset = StockReceive.objects.select_related('item', 'vendor')
    serializer_class = StockReceiveSerializer
    related_college_lookup = 'item__college_id'
    filterset_fields = ['item', 'vendor', 'receive_date', 'is_active']
    ordering_fields = ['receive_date', 'created_at']
    ordering = ['-receive_date']


class StoreSaleViewSet(CollegeScopedModelViewSet):
    queryset = StoreSale.objects.select_related('college', 'student', 'teacher', 'sold_by').all_colleges()
    serializer_class = StoreSaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'teacher', 'payment_status', 'sale_date', 'is_active']
    ordering_fields = ['sale_date', 'total_amount', 'created_at']
    ordering = ['-sale_date']


class SaleItemViewSet(RelatedCollegeScopedModelViewSet):
    queryset = SaleItem.objects.select_related('sale', 'item')
    serializer_class = SaleItemSerializer
    related_college_lookup = 'sale__college_id'
    filterset_fields = ['sale', 'item', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class PrintJobViewSet(CollegeScopedModelViewSet):
    queryset = PrintJob.objects.select_related('college', 'teacher').all_colleges()
    serializer_class = PrintJobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher', 'status', 'submission_date', 'completion_date', 'is_active']
    search_fields = ['job_name']
    ordering_fields = ['submission_date', 'completion_date', 'total_amount', 'created_at']
    ordering = ['-submission_date']


class StoreCreditViewSet(RelatedCollegeScopedModelViewSet):
    queryset = StoreCredit.objects.select_related('student')
    serializer_class = StoreCreditSerializer
    related_college_lookup = 'student__college_id'
    filterset_fields = ['student', 'transaction_type', 'date', 'is_active']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
