import os

from rest_framework import serializers
from django.utils import timezone

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
    CollegeStore,
    ProcurementRequirement,
    RequirementItem,
    SupplierQuotation,
    QuotationItem,
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceiptNote,
    GoodsReceiptItem,
    InspectionNote,
    StoreIndent,
    IndentItem,
    MaterialIssueNote,
    MaterialIssueItem,
    CentralStoreInventory,
    InventoryTransaction,
)


MAX_QUOTATION_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_QUOTATION_CONTENT_TYPES = {'application/pdf', 'image/jpeg', 'image/png'}
ALLOWED_QUOTATION_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}


def _validate_quotation_file(value):
    if not value:
        return value
    if value.size > MAX_QUOTATION_FILE_SIZE:
        raise serializers.ValidationError('Quotation file must be 5 MB or smaller.')
    content_type = getattr(value, 'content_type', None)
    if content_type:
        content_type = content_type.lower()
        if content_type not in ALLOWED_QUOTATION_CONTENT_TYPES:
            raise serializers.ValidationError('Only PDF or image files are allowed.')
    name = getattr(value, 'name', '')
    ext = os.path.splitext(name)[1].lower() if name else ''
    if ext and ext not in ALLOWED_QUOTATION_EXTENSIONS:
        raise serializers.ValidationError('Only PDF or image files are allowed.')
    if not content_type and not ext:
        raise serializers.ValidationError('Only PDF or image files are allowed.')
    return value


class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCategory
        fields = '__all__'


class StoreItemSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True, allow_null=True)
    class Meta:
        model = StoreItem
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        stock_quantity = attrs.get('stock_quantity')
        if self.instance and stock_quantity is None:
            stock_quantity = self.instance.stock_quantity
        if stock_quantity is not None and stock_quantity < 0:
            raise serializers.ValidationError({
                'stock_quantity': 'Stock quantity cannot be negative.'
            })
        return attrs


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class StockReceiveSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True, allow_null=True)
    class Meta:
        model = StockReceive
        fields = '__all__'


class StoreSaleSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True, allow_null=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True, allow_null=True)
    sold_by_name = serializers.CharField(source='sold_by.get_full_name', read_only=True, allow_null=True)
    class Meta:
        model = StoreSale
        fields = '__all__'


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        item = attrs.get('item')
        quantity = attrs.get('quantity')
        if self.instance:
            if item is None:
                item = self.instance.item
            if quantity is None:
                quantity = self.instance.quantity
        if item and quantity is not None:
            if (item.stock_quantity or 0) <= 0:
                raise serializers.ValidationError({'quantity': 'Required stock not available.'})
            if quantity > item.stock_quantity:
                raise serializers.ValidationError({
                    'quantity': f'Required stock not available. Available: {item.stock_quantity}'
                })
        return attrs


class PrintJobSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    class Meta:
        model = PrintJob
        fields = '__all__'


class StoreCreditSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    class Meta:
        model = StoreCredit
        fields = '__all__'


class SupplierMasterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierMaster
        fields = ['id', 'supplier_code', 'name', 'supplier_type', 'rating', 'is_active']


class SupplierMasterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierMaster
        fields = '__all__'


class SupplierMasterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierMaster
        fields = '__all__'


class SupplierMasterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierMaster
        exclude = ['supplier_code']


class CentralStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CentralStore
        fields = '__all__'


class CentralStoreListSerializer(serializers.ModelSerializer):
    """List all stores with manager and creation details"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    store_type = serializers.SerializerMethodField()

    class Meta:
        model = CentralStore
        fields = '__all__'

    def get_store_type(self, obj):
        return 'Central Store'


class CollegeStoreSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, allow_null=True)
    class Meta:
        model = CollegeStore
        fields = '__all__'


class CollegeStoreListSerializer(serializers.ModelSerializer):
    """List college stores with manager details"""
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, allow_null=True)
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = CollegeStore
        fields = '__all__'


class RequirementItemSerializer(serializers.ModelSerializer):
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    class Meta:
        model = RequirementItem
        fields = '__all__'


class RequirementItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequirementItem
        exclude = ['requirement']


class ProcurementRequirementListSerializer(serializers.ModelSerializer):
    is_draft_submitted = serializers.SerializerMethodField()
    is_quotation_approved = serializers.SerializerMethodField()
    is_po_created = serializers.SerializerMethodField()
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)

    class Meta:
        model = ProcurementRequirement
        fields = ['id', 'requirement_number', 'title', 'status', 'urgency', 'requirement_date',
                  'required_by_date', 'central_store', 'central_store_name', 'is_draft_submitted', 'is_quotation_approved', 'is_po_created']

    def get_is_draft_submitted(self, obj):
        return obj.status in ['submitted', 'pending_approval', 'approved', 'quotations_received', 'po_created', 'fulfilled']

    def get_is_quotation_approved(self, obj):
        return obj.quotations.filter(is_selected=True).exists()

    def get_is_po_created(self, obj):
        return obj.status in ['po_created', 'fulfilled']


class ProcurementRequirementDetailSerializer(serializers.ModelSerializer):
    items = RequirementItemSerializer(many=True, read_only=True)
    quotations_count = serializers.SerializerMethodField()

    class Meta:
        model = ProcurementRequirement
        fields = '__all__'

    def get_quotations_count(self, obj):
        return obj.quotations.count()


class ProcurementRequirementCreateSerializer(serializers.ModelSerializer):
    items = RequirementItemCreateSerializer(many=True)

    class Meta:
        model = ProcurementRequirement
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        requirement = ProcurementRequirement.objects.create(**validated_data)
        for item_data in items_data:
            RequirementItem.objects.create(requirement=requirement, **item_data)
        return requirement


class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = '__all__'


class QuotationItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        exclude = ['quotation']


class SupplierQuotationListSerializer(serializers.ModelSerializer):
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    quotation_file_url = serializers.SerializerMethodField()

    def get_quotation_file_url(self, obj):
        if not obj.quotation_file:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.quotation_file.url)
        return obj.quotation_file.url

    class Meta:
        model = SupplierQuotation
        fields = ['id', 'quotation_number', 'requirement', 'requirement_number', 'supplier', 'supplier_name',
                  'quotation_date', 'status', 'is_selected', 'quotation_file_url']


class SupplierQuotationDetailSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    supplier_details = SupplierMasterDetailSerializer(source='supplier', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    requirement_title = serializers.CharField(source='requirement.title', read_only=True)

    class Meta:
        model = SupplierQuotation
        fields = '__all__'

    def validate_quotation_file(self, value):
        return _validate_quotation_file(value)


class SupplierQuotationCreateSerializer(serializers.ModelSerializer):
    quotation_date = serializers.DateField(required=False, allow_null=True)
    valid_until = serializers.DateField(required=False, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=SupplierMaster.objects.all(), required=False, allow_null=True)

    class Meta:
        model = SupplierQuotation
        fields = '__all__'
        read_only_fields = ['quotation_number', 'status', 'is_selected']

    def validate_quotation_file(self, value):
        return _validate_quotation_file(value)

    def create(self, validated_data):
        if not validated_data.get('quotation_date'):
            validated_data['quotation_date'] = timezone.now().date()
        if not validated_data.get('valid_until'):
            validated_data['valid_until'] = validated_data['quotation_date']

        total_amount = validated_data.get('total_amount')
        tax_amount = validated_data.get('tax_amount')
        grand_total = validated_data.get('grand_total')

        if total_amount is None:
            validated_data['total_amount'] = 0
        if tax_amount is None:
            validated_data['tax_amount'] = 0
        if grand_total is None:
            validated_data['grand_total'] = (validated_data.get('total_amount') or 0) + (validated_data.get('tax_amount') or 0)

        if not validated_data.get('supplier'):
            supplier = SupplierMaster.objects.filter(is_active=True).first()
            if not supplier:
                raise serializers.ValidationError({'supplier': 'No active supplier available to use as default.'})
            validated_data['supplier'] = supplier

        return super().create(validated_data)


class SupplierQuotationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuotation
        fields = '__all__'
        extra_kwargs = {
            'quotation_number': {'required': False},
            'quotation_date': {'required': False},
            'requirement': {'required': False},
            'supplier': {'required': False},
            'valid_until': {'required': False},
            'total_amount': {'required': False},
            'tax_amount': {'required': False},
            'grand_total': {'required': False},
        }

    def validate_quotation_file(self, value):
        return _validate_quotation_file(value)



class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'


class PurchaseOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        exclude = ['purchase_order']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'supplier_name', 'requirement_number', 'central_store_name',
                  'status', 'po_date', 'expected_delivery_date']


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    quotation_number = serializers.CharField(source='quotation.quotation_number', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_details = SupplierMasterDetailSerializer(source='supplier', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemCreateSerializer(many=True, required=False)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        po = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=po, **item_data)
        return po


class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    po_number = serializers.CharField(source='po_item.purchase_order.po_number', read_only=True)
    class Meta:
        model = GoodsReceiptItem
        fields = '__all__'


class GoodsReceiptItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptItem
        exclude = ['grn']


class GoodsReceiptNoteListSerializer(serializers.ModelSerializer):
    purchase_order_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    class Meta:
        model = GoodsReceiptNote
        fields = ['id', 'grn_number', 'purchase_order', 'purchase_order_number', 'supplier_name',
                  'central_store_name', 'status', 'receipt_date']


class GoodsReceiptNoteDetailSerializer(serializers.ModelSerializer):
    purchase_order_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True, allow_null=True)
    items = GoodsReceiptItemSerializer(many=True, read_only=True)
    inspection = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GoodsReceiptNote
        fields = '__all__'


class GoodsReceiptNoteCreateSerializer(serializers.ModelSerializer):
    items = GoodsReceiptItemCreateSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptNote
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        grn = GoodsReceiptNote.objects.create(**validated_data)
        for item_data in items_data:
            GoodsReceiptItem.objects.create(grn=grn, **item_data)
        return grn


class InspectionNoteSerializer(serializers.ModelSerializer):
    grn_number = serializers.CharField(source='grn.grn_number', read_only=True)
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True, allow_null=True)
    class Meta:
        model = InspectionNote
        fields = '__all__'


class IndentItemSerializer(serializers.ModelSerializer):
    indent_number = serializers.CharField(source='indent.indent_number', read_only=True)
    available_stock_in_central = serializers.SerializerMethodField()
    central_store_item_name = serializers.CharField(source='central_store_item.name', read_only=True)

    class Meta:
        model = IndentItem
        fields = '__all__'

    def get_available_stock_in_central(self, obj):
        """Phase 8.6: Include method field available_stock_in_central"""
        try:
            if obj.indent and obj.indent.central_store and obj.central_store_item:
                from .models import CentralStoreInventory
                inventory = CentralStoreInventory.objects.get(
                    central_store=obj.indent.central_store,
                    item=obj.central_store_item
                )
                return inventory.quantity_available
        except Exception:
            return 0
        return None


class IndentItemCreateSerializer(serializers.ModelSerializer):
    central_store_item = serializers.PrimaryKeyRelatedField(
        queryset=StoreItem.objects.none()
    )

    class Meta:
        model = IndentItem
        exclude = ['indent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow all store items from any college
        from .models import StoreItem
        self.fields['central_store_item'].queryset = StoreItem.objects.all_colleges()


class StoreIndentListSerializer(serializers.ModelSerializer):
    requesting_store_manager_name = serializers.CharField(source='requesting_store_manager.get_full_name', read_only=True, allow_null=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_prepared = serializers.SerializerMethodField()
    is_dispatched = serializers.SerializerMethodField()
    is_in_transit = serializers.SerializerMethodField()
    is_received = serializers.SerializerMethodField()

    class Meta:
        model = StoreIndent
        fields = ['id', 'indent_number', 'college', 'college_name', 'central_store',
                  'central_store_name', 'requesting_store_manager_name', 'status', 'status_display', 'priority',
                  'indent_date', 'is_prepared', 'is_dispatched', 'is_in_transit', 'is_received']

    def _get_issue_flag(self, obj, attr, status):
        value = getattr(obj, attr, None)
        if value is not None:
            return bool(value)
        return obj.material_issues.filter(status=status).exists()

    def get_is_prepared(self, obj):
        return self._get_issue_flag(obj, 'has_prepared', 'prepared')

    def get_is_dispatched(self, obj):
        return self._get_issue_flag(obj, 'has_dispatched', 'dispatched')

    def get_is_in_transit(self, obj):
        return self._get_issue_flag(obj, 'has_in_transit', 'in_transit')

    def get_is_received(self, obj):
        return self._get_issue_flag(obj, 'has_received', 'received')


class StoreIndentDetailSerializer(serializers.ModelSerializer):
    items = IndentItemSerializer(many=True, read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requesting_store_manager_name = serializers.CharField(source='requesting_store_manager.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = StoreIndent
        fields = '__all__'


class StoreIndentCreateSerializer(serializers.ModelSerializer):
    items = IndentItemCreateSerializer(many=True)

    class Meta:
        model = StoreIndent
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        central_store = attrs.get('central_store')
        items_data = attrs.get('items', [])
        if central_store and items_data:
            from .models import CentralStoreInventory
            item_errors = []
            has_errors = False
            for item_data in items_data:
                errors = {}
                central_item = item_data.get('central_store_item')
                requested_qty = item_data.get('requested_quantity')
                inventory = None
                if central_item:
                    inventory = CentralStoreInventory.objects.filter(
                        central_store=central_store,
                        item=central_item
                    ).first()
                if not inventory or (inventory.quantity_available or 0) <= 0:
                    errors['requested_quantity'] = 'Required stock not available in central inventory.'
                elif requested_qty and requested_qty > inventory.quantity_available:
                    errors['requested_quantity'] = (
                        f'Required stock not available in central inventory. '
                        f'Available: {inventory.quantity_available}'
                    )
                if errors:
                    has_errors = True
                item_errors.append(errors)
            if has_errors:
                raise serializers.ValidationError({'items': item_errors})
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        indent = StoreIndent.objects.create(**validated_data)
        for item_data in items_data:
            IndentItem.objects.create(indent=indent, **item_data)
        return indent


class MaterialIssueItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    indent_number = serializers.CharField(source='material_issue.indent.indent_number', read_only=True)
    class Meta:
        model = MaterialIssueItem
        fields = '__all__'


class MaterialIssueItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialIssueItem
        exclude = ['material_issue']


class MaterialIssueNoteListSerializer(serializers.ModelSerializer):
    indent_number = serializers.CharField(source='indent.indent_number', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    receiving_college_name = serializers.CharField(source='receiving_college.name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.get_full_name', read_only=True, allow_null=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True, allow_null=True)
    items = MaterialIssueItemSerializer(many=True, read_only=True)
    class Meta:
        model = MaterialIssueNote
        fields = '__all__'


class MaterialIssueNoteDetailSerializer(serializers.ModelSerializer):
    items = MaterialIssueItemSerializer(many=True, read_only=True)

    class Meta:
        model = MaterialIssueNote
        fields = '__all__'


class MaterialIssueNoteCreateSerializer(serializers.ModelSerializer):
    items = MaterialIssueItemCreateSerializer(many=True, required=False)

    class Meta:
        model = MaterialIssueNote
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        central_store = attrs.get('central_store')
        items_data = attrs.get('items', [])
        if central_store and items_data:
            from .models import CentralStoreInventory
            item_errors = []
            has_errors = False
            for item_data in items_data:
                errors = {}
                item = item_data.get('item')
                issued_qty = item_data.get('issued_quantity')
                indent_item = item_data.get('indent_item')
                expected_qty = None
                if indent_item:
                    expected_qty = (
                        indent_item.pending_quantity
                        or indent_item.approved_quantity
                        or indent_item.requested_quantity
                    )
                inventory = None
                if item:
                    inventory = CentralStoreInventory.objects.filter(
                        central_store=central_store,
                        item=item
                    ).first()
                if expected_qty is not None and issued_qty is not None:
                    if issued_qty != expected_qty:
                        errors['issued_quantity'] = (
                            f'Issued quantity must fully fulfill the request. Expected: {expected_qty}.'
                        )
                if not inventory or (inventory.quantity_available or 0) <= 0:
                    errors['issued_quantity'] = 'Required stock not available in central inventory.'
                else:
                    qty_to_check = expected_qty if expected_qty is not None else issued_qty
                    if qty_to_check is not None and qty_to_check > inventory.quantity_available:
                        errors['issued_quantity'] = (
                            f'Required stock not available in central inventory. '
                            f'Available: {inventory.quantity_available}'
                        )
                if errors:
                    has_errors = True
                item_errors.append(errors)
            if has_errors:
                raise serializers.ValidationError({'items': item_errors})
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        min_note = MaterialIssueNote.objects.create(**validated_data)
        for item_data in items_data:
            MaterialIssueItem.objects.create(material_issue=min_note, **item_data)
        return min_note


class CentralStoreInventoryListSerializer(serializers.ModelSerializer):
    """For GET - returns item ID and name"""
    item_display = serializers.CharField(source='item.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)

    class Meta:
        model = CentralStoreInventory
        fields = ['id', 'item', 'item_display', 'central_store', 'central_store_name',
                  'quantity_on_hand', 'quantity_allocated', 'quantity_available',
                  'min_stock_level', 'reorder_point', 'max_stock_level',
                  'last_stock_update', 'unit_cost', 'is_active',
                  'created_at', 'updated_at']


class CentralStoreInventoryCreateSerializer(serializers.ModelSerializer):
    """For POST - only accepts item_name"""
    item_name = serializers.CharField(write_only=True)

    class Meta:
        model = CentralStoreInventory
        fields = ['item_name', 'central_store', 'quantity_on_hand',
                  'quantity_allocated', 'quantity_available', 'min_stock_level',
                  'reorder_point', 'max_stock_level', 'unit_cost', 'is_active']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        quantity_on_hand = attrs.get('quantity_on_hand')
        quantity_allocated = attrs.get('quantity_allocated')
        if quantity_on_hand is not None and quantity_on_hand < 0:
            raise serializers.ValidationError({
                'quantity_on_hand': 'Stock cannot go negative.'
            })
        if quantity_allocated is not None and quantity_allocated < 0:
            raise serializers.ValidationError({
                'quantity_allocated': 'Allocated quantity cannot be negative.'
            })
        if quantity_on_hand is not None and quantity_allocated is not None:
            if quantity_allocated > quantity_on_hand:
                raise serializers.ValidationError({
                    'quantity_allocated': 'Allocated quantity cannot exceed on-hand quantity.'
                })
        return attrs

    def create(self, validated_data):
        item_name = validated_data.pop('item_name')
        from .models import StoreItem, StoreCategory

        # Find or create item
        item = StoreItem.objects.all_colleges().filter(name__iexact=item_name).first()
        if not item:
            # Auto-create item for central inventory
            category, _ = StoreCategory.objects.get_or_create(
                name='General',
                defaults={'code': 'GEN', 'college_id': 1}
            )
            item = StoreItem.objects.create(
                name=item_name,
                code=item_name.upper()[:20],
                category=category,
                unit='unit',
                price=0,
                managed_by='central',
                college_id=1
            )
        validated_data['item'] = item
        return super().create(validated_data)


class CentralStoreInventorySerializer(CentralStoreInventoryListSerializer):
    """Default - same as list"""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        quantity_on_hand = attrs.get('quantity_on_hand')
        quantity_allocated = attrs.get('quantity_allocated')
        if self.instance:
            if quantity_on_hand is None:
                quantity_on_hand = self.instance.quantity_on_hand
            if quantity_allocated is None:
                quantity_allocated = self.instance.quantity_allocated
        if quantity_on_hand is not None and quantity_on_hand < 0:
            raise serializers.ValidationError({
                'quantity_on_hand': 'Stock cannot go negative.'
            })
        if quantity_allocated is not None and quantity_allocated < 0:
            raise serializers.ValidationError({
                'quantity_allocated': 'Allocated quantity cannot be negative.'
            })
        if quantity_on_hand is not None and quantity_allocated is not None:
            if quantity_allocated > quantity_on_hand:
                raise serializers.ValidationError({
                    'quantity_allocated': 'Allocated quantity cannot exceed on-hand quantity.'
                })
        return attrs


class InventoryTransactionSerializer(serializers.ModelSerializer):
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True, allow_null=True)
    reference_type_name = serializers.CharField(source='reference_type.model', read_only=True, allow_null=True)
    class Meta:
        model = InventoryTransaction
        fields = '__all__'


class StockSummarySerializer(serializers.Serializer):
    central_store = serializers.IntegerField()
    total_items = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
