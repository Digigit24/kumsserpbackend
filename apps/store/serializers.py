from rest_framework import serializers

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


class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCategory
        fields = '__all__'


class StoreItemSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = StockReceive
        fields = '__all__'


class StoreSaleSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = PrintJob
        fields = '__all__'


class StoreCreditSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = ProcurementRequirement
        fields = ['id', 'requirement_number', 'title', 'status', 'urgency', 'requirement_date',
                  'required_by_date', 'central_store', 'is_draft_submitted', 'is_quotation_approved', 'is_po_created']

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
    class Meta:
        model = SupplierQuotation
        fields = ['id', 'quotation_number', 'requirement', 'supplier', 'quotation_date', 'status', 'is_selected']


class SupplierQuotationDetailSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    supplier_details = SupplierMasterDetailSerializer(source='supplier', read_only=True)

    class Meta:
        model = SupplierQuotation
        fields = '__all__'


class SupplierQuotationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuotation
        fields = ['quotation_file']  # Only accept file upload


class QuotationComparisonSerializer(serializers.Serializer):
    quotation = SupplierQuotationDetailSerializer()


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'


class PurchaseOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        exclude = ['purchase_order']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'status', 'po_date', 'expected_delivery_date']


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = GoodsReceiptItem
        fields = '__all__'


class GoodsReceiptItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptItem
        exclude = ['grn']


class GoodsReceiptNoteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptNote
        fields = ['id', 'grn_number', 'purchase_order', 'status', 'receipt_date']


class GoodsReceiptNoteDetailSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = InspectionNote
        fields = '__all__'


class IndentItemSerializer(serializers.ModelSerializer):
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
                  'central_store_name', 'status', 'status_display', 'priority', 'indent_date',
                  'is_prepared', 'is_dispatched', 'is_in_transit', 'is_received']

    def get_is_prepared(self, obj):
        return obj.material_issues.filter(status='prepared').exists()

    def get_is_dispatched(self, obj):
        return obj.material_issues.filter(status='dispatched').exists()

    def get_is_in_transit(self, obj):
        return obj.material_issues.filter(status='in_transit').exists()

    def get_is_received(self, obj):
        return obj.material_issues.filter(status='received').exists()


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
    class Meta:
        model = MaterialIssueItem
        fields = '__all__'


class MaterialIssueItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialIssueItem
        exclude = ['material_issue']


class MaterialIssueNoteListSerializer(serializers.ModelSerializer):
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
                inventory = None
                if item:
                    inventory = CentralStoreInventory.objects.filter(
                        central_store=central_store,
                        item=item
                    ).first()
                if not inventory or (inventory.quantity_available or 0) <= 0:
                    errors['issued_quantity'] = 'Required stock not available in central inventory.'
                elif issued_qty and issued_qty > inventory.quantity_available:
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

    class Meta:
        model = CentralStoreInventory
        fields = ['id', 'item', 'item_display', 'central_store',
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
    class Meta:
        model = InventoryTransaction
        fields = '__all__'


class StockSummarySerializer(serializers.Serializer):
    central_store = serializers.IntegerField()
    total_items = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
