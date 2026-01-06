from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models

from apps.core.mixins import (
    CollegeScopedMixin, CollegeScopedModelViewSet, RelatedCollegeScopedModelViewSet
)
from .models import (
    StoreCategory,
    StoreItem,
    Vendor,
    StockReceive,
    StoreSale,
    SaleItem,
    PrintJob,
    StoreCredit,
    SupplierMaster,
    CentralStore,
    ProcurementRequirement,
    SupplierQuotation,
    PurchaseOrder,
    GoodsReceiptNote,
    InspectionNote,
    StoreIndent,
    MaterialIssueNote,
    CentralStoreInventory,
    InventoryTransaction,
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
    SupplierMasterListSerializer,
    SupplierMasterDetailSerializer,
    SupplierMasterCreateSerializer,
    SupplierMasterUpdateSerializer,
    CentralStoreSerializer,
    CentralStoreListSerializer,
    ProcurementRequirementListSerializer,
    ProcurementRequirementDetailSerializer,
    ProcurementRequirementCreateSerializer,
    SupplierQuotationListSerializer,
    SupplierQuotationDetailSerializer,
    SupplierQuotationCreateSerializer,
    PurchaseOrderListSerializer,
    PurchaseOrderDetailSerializer,
    PurchaseOrderCreateSerializer,
    GoodsReceiptNoteListSerializer,
    GoodsReceiptNoteDetailSerializer,
    GoodsReceiptNoteCreateSerializer,
    InspectionNoteSerializer,
    StoreIndentListSerializer,
    StoreIndentDetailSerializer,
    StoreIndentCreateSerializer,
    MaterialIssueNoteListSerializer,
    MaterialIssueNoteDetailSerializer,
    MaterialIssueNoteCreateSerializer,
    CentralStoreInventorySerializer,
    CentralStoreInventoryCreateSerializer,
    InventoryTransactionSerializer,
)
from .permissions import (
    IsCentralStoreManagerOrReadOnly,
    IsCentralStoreManager,
    IsCollegeStoreManager,
    IsCEOOrFinance,
    CanApproveIndent,
    CanReceiveMaterials,
)
from .utils import generate_po_pdf, generate_min_pdf, generate_grn_pdf


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
    queryset = StoreItem.objects.all_colleges().select_related('category', 'college')
    serializer_class = StoreItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'managed_by', 'central_store']
    search_fields = ['name', 'code', 'barcode']
    ordering_fields = ['name', 'stock_quantity', 'min_stock_level', 'price', 'created_at']
    ordering = ['name']

    def create(self, request, *args, **kwargs):
        """Prevent college_admin from creating central store items"""
        from rest_framework.exceptions import PermissionDenied

        # Check if user is trying to create a central store item
        managed_by = request.data.get('managed_by', 'college')
        if managed_by == 'central' and request.user.user_type == 'college_admin':
            raise PermissionDenied("College admins cannot create central store items")

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Prevent college_admin from updating items to central"""
        from rest_framework.exceptions import PermissionDenied

        managed_by = request.data.get('managed_by')
        if managed_by == 'central' and request.user.user_type == 'college_admin':
            raise PermissionDenied("College admins cannot modify central store items")

        return super().update(request, *args, **kwargs)


class VendorViewSet(CollegeScopedModelViewSet):
    queryset = Vendor.objects.all_colleges().select_related('college')
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
    queryset = StoreSale.objects.all_colleges().select_related('college', 'student', 'teacher', 'sold_by')
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
    queryset = PrintJob.objects.all_colleges().select_related('college', 'teacher')
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


class SupplierMasterViewSet(viewsets.ModelViewSet):
    queryset = SupplierMaster.objects.all()
    permission_classes = [IsCentralStoreManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'supplier_type', 'rating']
    search_fields = ['name', 'supplier_code', 'gstin', 'city']
    ordering_fields = ['name', 'rating', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierMasterListSerializer
        if self.action in ['create']:
            return SupplierMasterCreateSerializer
        if self.action in ['update', 'partial_update']:
            return SupplierMasterUpdateSerializer
        return SupplierMasterDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsCentralStoreManager])
    def verify(self, request, pk=None):
        supplier = self.get_object()
        supplier.is_verified = True
        supplier.verification_date = supplier.verification_date or supplier.updated_at
        supplier.save(update_fields=['is_verified', 'verification_date', 'updated_at'])
        return Response({'status': 'verified'})


class CentralStoreViewSet(viewsets.ModelViewSet):
    queryset = CentralStore.objects.select_related('manager').all()
    serializer_class = CentralStoreSerializer
    permission_classes = [IsCentralStoreManagerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'city']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return CentralStoreListSerializer
        return CentralStoreSerializer

    @action(detail=True, methods=['get'], permission_classes=[IsCentralStoreManager])
    def inventory(self, request, pk=None):
        store = self.get_object()
        qs = CentralStoreInventory.objects.filter(central_store=store)
        serializer = CentralStoreInventorySerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsCentralStoreManager])
    def stock_summary(self, request, pk=None):
        store = self.get_object()
        qs = CentralStoreInventory.objects.filter(central_store=store)
        total_items = qs.count()
        total_qty = sum(item.quantity_on_hand for item in qs)
        return Response({'central_store': store.id, 'total_items': total_items, 'total_quantity': total_qty})

    @action(detail=True, methods=['get'], permission_classes=[IsCentralStoreManager])
    def low_stock_alerts(self, request, pk=None):
        """Phase 9.10: GET items below reorder point"""
        store = self.get_object()
        qs = CentralStoreInventory.objects.filter(
            central_store=store,
            quantity_available__lte=models.F('reorder_point')
        )
        serializer = CentralStoreInventorySerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsCentralStoreManager])
    def pending_indents(self, request, pk=None):
        """Phase 9.10: GET all pending indent approvals"""
        store = self.get_object()
        indents = StoreIndent.objects.filter(
            central_store=store,
            status='pending_approval'
        )
        from .serializers import StoreIndentListSerializer
        serializer = StoreIndentListSerializer(indents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='list', permission_classes=[IsCentralStoreManager])
    def stores_list(self, request):
        """GET /api/v1/store/central-stores/list/ - List all stores"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = CentralStoreListSerializer(queryset, many=True)
        return Response(serializer.data)


class ProcurementRequirementViewSet(viewsets.ModelViewSet):
    queryset = ProcurementRequirement.objects.all().select_related('central_store')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'urgency', 'requirement_date']
    search_fields = ['requirement_number', 'title']
    ordering_fields = ['requirement_date', 'required_by_date', 'created_at']
    ordering = ['-requirement_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProcurementRequirementListSerializer
        if self.action == 'create':
            return ProcurementRequirementCreateSerializer
        return ProcurementRequirementDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_for_approval(self, request, pk=None):
        obj = self.get_object()
        obj.submit_for_approval()
        return Response({'status': obj.status})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def quotations(self, request, pk=None):
        obj = self.get_object()
        serializer = SupplierQuotationListSerializer(obj.quotations.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def compare_quotations(self, request, pk=None):
        """Phase 9.3: GET side-by-side comparison data"""
        obj = self.get_object()
        quotations = obj.quotations.all()
        comparison_data = []
        for quot in quotations:
            comparison_data.append({
                'quotation': SupplierQuotationDetailSerializer(quot).data,
                'supplier': SupplierMasterDetailSerializer(quot.supplier).data,
            })
        return Response(comparison_data)

    @action(detail=True, methods=['post'], permission_classes=[IsCEOOrFinance])
    def select_quotation(self, request, pk=None):
        obj = self.get_object()
        quotation_id = request.data.get('quotation_id')
        quotation = obj.quotations.filter(id=quotation_id).first()
        if not quotation:
            return Response({'detail': 'Quotation not found'}, status=status.HTTP_404_NOT_FOUND)
        quotation.mark_as_selected()
        obj.status = 'approved'
        obj.save(update_fields=['status', 'updated_at'])
        return Response({'status': 'quotation_selected', 'quotation': quotation.id})


class SupplierQuotationViewSet(viewsets.ModelViewSet):
    queryset = SupplierQuotation.objects.all().select_related('requirement', 'supplier')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['requirement', 'supplier', 'status', 'is_selected']
    search_fields = ['quotation_number']
    ordering_fields = ['quotation_date', 'created_at']
    ordering = ['-quotation_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsCentralStoreManager()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierQuotationListSerializer
        if self.action == 'create':
            return SupplierQuotationCreateSerializer
        return SupplierQuotationDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsCentralStoreManager])
    def mark_selected(self, request, pk=None):
        quotation = self.get_object()
        quotation.mark_as_selected()
        return Response({'status': 'selected'})


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().select_related('requirement', 'supplier', 'central_store')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier', 'po_date']
    search_fields = ['po_number']
    ordering_fields = ['po_date', 'created_at']
    ordering = ['-po_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'send_to_supplier', 'acknowledge', 'generate_pdf']:
            return [IsCentralStoreManager()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderDetailSerializer

    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        po = self.get_object()
        generate_po_pdf(po)
        return Response({'status': 'pdf_generated'})

    @action(detail=True, methods=['post'])
    def send_to_supplier(self, request, pk=None):
        po = self.get_object()
        po.send_to_supplier()
        return Response({'status': po.status})

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        po = self.get_object()
        po.mark_as_acknowledged()
        return Response({'status': po.status})


class GoodsReceiptNoteViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceiptNote.objects.all().select_related('purchase_order', 'supplier', 'central_store')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase_order', 'status', 'receipt_date']
    search_fields = ['grn_number']
    ordering_fields = ['receipt_date', 'created_at']
    ordering = ['-receipt_date']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'submit_for_inspection', 'post_to_inventory']:
            return [IsCentralStoreManager()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return GoodsReceiptNoteListSerializer
        if self.action == 'create':
            return GoodsReceiptNoteCreateSerializer
        return GoodsReceiptNoteDetailSerializer

    @action(detail=True, methods=['post'])
    def submit_for_inspection(self, request, pk=None):
        grn = self.get_object()
        grn.submit_for_inspection()
        return Response({'status': grn.status})

    @action(detail=True, methods=['post'])
    def post_to_inventory(self, request, pk=None):
        grn = self.get_object()
        grn.post_to_inventory()
        generate_grn_pdf(grn)
        return Response({'status': grn.status})


class InspectionNoteViewSet(viewsets.ModelViewSet):
    queryset = InspectionNote.objects.all().select_related('grn')
    serializer_class = InspectionNoteSerializer
    permission_classes = [IsCentralStoreManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['overall_status']
    ordering_fields = ['inspection_date', 'created_at']
    ordering = ['-inspection_date']


class StoreIndentViewSet(CollegeScopedModelViewSet):
    queryset = StoreIndent.objects.all_colleges().select_related('college', 'central_store')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'college', 'priority', 'indent_date']
    search_fields = ['indent_number']
    ordering_fields = ['indent_date', 'created_at']
    ordering = ['-indent_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return StoreIndentListSerializer
        if self.action == 'create':
            return StoreIndentCreateSerializer
        return StoreIndentDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """College store manager submits indent to college admin"""
        indent = self.get_object()
        indent.submit()
        return Response({'status': indent.status, 'message': 'Submitted to college admin for approval'})

    @action(detail=True, methods=['post'], permission_classes=[CanApproveIndent])
    def college_admin_approve(self, request, pk=None):
        """College admin approves and forwards to super admin"""
        indent = self.get_object()
        # Verify user is college admin for this college
        if not request.user.is_superuser and indent.college_id != getattr(request.user, 'college_id', None):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        indent.college_admin_approve(user=request.user)
        return Response({'status': indent.status, 'message': 'Forwarded to super admin for approval'})

    @action(detail=True, methods=['post'], permission_classes=[CanApproveIndent])
    def college_admin_reject(self, request, pk=None):
        """College admin rejects the indent"""
        indent = self.get_object()
        if not request.user.is_superuser and indent.college_id != getattr(request.user, 'college_id', None):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        indent.college_admin_reject(user=request.user, reason=request.data.get('reason'))
        return Response({'status': indent.status, 'message': 'Rejected by college admin'})

    @action(detail=True, methods=['post'], permission_classes=[IsCentralStoreManager])
    def super_admin_approve(self, request, pk=None):
        """Super admin approves and forwards to central store"""
        indent = self.get_object()
        indent.super_admin_approve(user=request.user)
        return Response({'status': indent.status, 'message': 'Approved by super admin, forwarded to central store'})

    @action(detail=True, methods=['post'], permission_classes=[IsCentralStoreManager])
    def super_admin_reject(self, request, pk=None):
        """Super admin rejects the indent"""
        indent = self.get_object()
        indent.super_admin_reject(user=request.user, reason=request.data.get('reason'))
        return Response({'status': indent.status, 'message': 'Rejected by super admin'})

    @action(detail=True, methods=['post'], permission_classes=[CanApproveIndent])
    def approve(self, request, pk=None):
        """Legacy approve - kept for backward compatibility"""
        indent = self.get_object()
        indent.approve(user=request.user)
        return Response({'status': indent.status})

    @action(detail=True, methods=['post'], permission_classes=[CanApproveIndent])
    def reject(self, request, pk=None):
        """Legacy reject - kept for backward compatibility"""
        indent = self.get_object()
        indent.reject(user=request.user, reason=request.data.get('reason'))
        return Response({'status': indent.status})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending_college_approvals(self, request):
        """For college admin, list indents pending their approval"""
        college_id = getattr(request.user, 'college_id', None)
        if request.user.is_superuser:
            indents = StoreIndent.objects.all_colleges().filter(status='pending_college_approval')
        elif college_id:
            indents = StoreIndent.objects.all_colleges().filter(status='pending_college_approval', college_id=college_id)
        else:
            indents = self.get_queryset().none()
        serializer = self.get_serializer(indents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsCentralStoreManager])
    def pending_super_admin_approvals(self, request):
        """For super admin, list indents pending their approval"""
        indents = StoreIndent.objects.all_colleges().filter(status='pending_super_admin')
        serializer = self.get_serializer(indents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[CanApproveIndent])
    def pending_approvals(self, request):
        """Legacy endpoint - list all pending indents"""
        indents = StoreIndent.objects.all_colleges().filter(status__in=['pending_college_approval', 'pending_super_admin'])
        serializer = self.get_serializer(indents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def approved(self, request):
        """List all approved indents (including super admin approved)"""
        college_id = getattr(request.user, 'college_id', None)
        indents = StoreIndent.objects.all_colleges().filter(
            status__in=['approved', 'super_admin_approved']
        )
        if not request.user.is_superuser and college_id:
            indents = indents.filter(college_id=college_id)
        
        serializer = self.get_serializer(indents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='partial', permission_classes=[IsAuthenticated])
    def partially_fulfilled(self, request):
        """List all partially fulfilled indents"""
        college_id = getattr(request.user, 'college_id', None)
        indents = StoreIndent.objects.all_colleges().filter(status='partially_fulfilled')
        if not request.user.is_superuser and college_id:
            indents = indents.filter(college_id=college_id)
            
        serializer = self.get_serializer(indents, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def fulfilled(self, request):
        """List all fulfilled indents"""
        college_id = getattr(request.user, 'college_id', None)
        indents = StoreIndent.objects.all_colleges().filter(status='fulfilled')
        if not request.user.is_superuser and college_id:
            indents = indents.filter(college_id=college_id)
            
        serializer = self.get_serializer(indents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsCentralStoreManager])
    def issue_materials(self, request, pk=None):
        """Phase 9.8: Create MaterialIssueNote (only after super admin approval)"""
        indent = self.get_object()
        if indent.status not in ['super_admin_approved', 'approved']:
            return Response(
                {'detail': 'Indent must be approved by super admin before issuing materials'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Create MaterialIssueNote
        issue_data = request.data.copy()
        issue_data['indent'] = indent.id
        issue_data['central_store'] = indent.central_store.id
        issue_data['receiving_college'] = indent.college.id
        serializer = MaterialIssueNoteCreateSerializer(data=issue_data)
        serializer.is_valid(raise_exception=True)
        min_note = serializer.save()
        return Response(MaterialIssueNoteDetailSerializer(min_note).data)


class MaterialIssueNoteViewSet(RelatedCollegeScopedModelViewSet):
    queryset = MaterialIssueNote.objects.select_related('indent', 'central_store', 'receiving_college')
    related_college_lookup = 'receiving_college_id'
    filterset_fields = ['status', 'receiving_college', 'issue_date']
    search_fields = ['min_number']
    ordering_fields = ['issue_date', 'created_at']
    ordering = ['-issue_date']

    def get_queryset(self):
        """Return all for superuser/central_manager, college-scoped for others"""
        user = self.request.user
        if user.is_superuser or getattr(user, 'user_type', None) == 'central_manager':
            return MaterialIssueNote.objects.select_related('indent', 'central_store', 'receiving_college')
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'dispatch']:
            return [IsCentralStoreManager()]
        if self.action in ['confirm_receipt']:
            return [CanReceiveMaterials()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return MaterialIssueNoteListSerializer
        if self.action == 'create':
            return MaterialIssueNoteCreateSerializer
        return MaterialIssueNoteDetailSerializer

    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        min_note = self.get_object()
        generate_min_pdf(min_note)
        return Response({'status': 'pdf_generated'})

    @action(detail=True, methods=['post'])
    def mark_dispatched(self, request, pk=None):
        min_note = self.get_object()
        min_note.dispatch()
        return Response({'status': min_note.status})

    @action(detail=True, methods=['post'])
    def confirm_receipt(self, request, pk=None):
        min_note = self.get_object()
        min_note.confirm_receipt(user=request.user, notes=request.data.get('notes'))
        return Response({'status': min_note.status})


class CentralStoreInventoryViewSet(viewsets.ModelViewSet):
    queryset = CentralStoreInventory.objects.select_related('central_store', 'item')
    serializer_class = CentralStoreInventorySerializer
    permission_classes = [IsAuthenticated]
    resource_name = 'store'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['central_store', 'item', 'quantity_available']
    ordering_fields = ['quantity_available', 'updated_at']
    ordering = ['quantity_available']

    def get_serializer_class(self):
        if self.action == 'create':
            return CentralStoreInventoryCreateSerializer
        return CentralStoreInventorySerializer

    def create(self, request, *args, **kwargs):
        """Only super admin can create central inventory"""
        if not request.user.is_superuser:
            return Response({'detail': 'Only super admin can add central inventory items'},
                          status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        qs = self.filter_queryset(self.get_queryset()).filter(quantity_available__lte=models.F('reorder_point'))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsCentralStoreManager])
    def adjust_stock(self, request, pk=None):
        inventory = self.get_object()
        delta = int(request.data.get('delta', 0))
        reason = request.data.get('remarks', '')
        inventory.update_stock(delta, 'adjustment', reference=None, performed_by=request.user)
        return Response({'quantity_on_hand': inventory.quantity_on_hand, 'quantity_available': inventory.quantity_available, 'reason': reason})


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryTransaction.objects.select_related('central_store', 'item')
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'transaction_date', 'item', 'central_store']
    search_fields = ['transaction_number']
    ordering_fields = ['-transaction_date']
    ordering = ['-transaction_date']
