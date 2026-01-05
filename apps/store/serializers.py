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
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = StoreCategory
        fields = '__all__'


class StoreItemSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)

    class Meta:
        model = StoreItem
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Vendor
        fields = '__all__'


class StockReceiveSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = StockReceive
        fields = '__all__'


class StoreSaleSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    sold_by_name = serializers.CharField(source='sold_by.get_full_name', read_only=True)

    class Meta:
        model = StoreSale
        fields = '__all__'


class SaleItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = '__all__'


class PrintJobSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    student_name = serializers.CharField(source='customer_student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='customer_teacher.get_full_name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)

    class Meta:
        model = PrintJob
        fields = '__all__'


class StoreCreditSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = StoreCredit
        fields = '__all__'


class SupplierMasterListSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = SupplierMaster
        fields = ['id', 'supplier_code', 'name', 'supplier_type', 'rating', 'is_active', 'college_name']


class SupplierMasterDetailSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)

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
    college_name = serializers.CharField(source='college.name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)

    class Meta:
        model = CentralStore
        fields = '__all__'


class RequirementItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = RequirementItem
        fields = '__all__'


class RequirementItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequirementItem
        exclude = ['requirement']


class ProcurementRequirementListSerializer(serializers.ModelSerializer):
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)

    class Meta:
        model = ProcurementRequirement
        fields = ['id', 'requirement_number', 'title', 'status', 'urgency', 'requirement_date', 'required_by_date', 'central_store', 'central_store_name']


class ProcurementRequirementDetailSerializer(serializers.ModelSerializer):
    items = RequirementItemSerializer(many=True, read_only=True)
    quotations_count = serializers.SerializerMethodField()
    college_name = serializers.CharField(source='college.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

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
    item_name = serializers.CharField(source='item.name', read_only=True)

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

    class Meta:
        model = SupplierQuotation
        fields = ['id', 'quotation_number', 'requirement', 'requirement_number', 'supplier', 'supplier_name', 'quotation_date', 'status', 'is_selected']


class SupplierQuotationDetailSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    supplier_details = SupplierMasterDetailSerializer(source='supplier', read_only=True)
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = SupplierQuotation
        fields = '__all__'


class SupplierQuotationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierQuotation
        fields = ['requirement', 'supplier', 'quotation_date', 'valid_until', 'total_amount', 'tax_amount', 'grand_total', 'quotation_file', 'notes']
        extra_kwargs = {
            'quotation_date': {'required': False},
            'valid_until': {'required': False},
            'total_amount': {'required': False},
            'grand_total': {'required': False},
        }

    def create(self, validated_data):
        # Set default values for required fields if not provided
        from datetime import date, timedelta
        if 'quotation_date' not in validated_data:
            validated_data['quotation_date'] = date.today()
        if 'valid_until' not in validated_data:
            validated_data['valid_until'] = date.today() + timedelta(days=30)
        if 'total_amount' not in validated_data:
            validated_data['total_amount'] = 0
        if 'grand_total' not in validated_data:
            validated_data['grand_total'] = validated_data.get('total_amount', 0) + validated_data.get('tax_amount', 0)
        
        return super().create(validated_data)


class QuotationComparisonSerializer(serializers.Serializer):
    quotation = SupplierQuotationDetailSerializer()


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = '__all__'


class PurchaseOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        exclude = ['purchase_order']


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_number', 'supplier', 'supplier_name', 'status', 'po_date', 'expected_delivery_date']


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_details = SupplierMasterDetailSerializer(source='supplier', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    quotation_number = serializers.CharField(source='quotation.quotation_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

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
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = GoodsReceiptItem
        fields = '__all__'


class GoodsReceiptItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptItem
        exclude = ['grn']


class GoodsReceiptNoteListSerializer(serializers.ModelSerializer):
    po_number = serializers.CharField(source='purchase_order.po_number', read_only=True)

    class Meta:
        model = GoodsReceiptNote
        fields = ['id', 'grn_number', 'purchase_order', 'po_number', 'status', 'receipt_date']


class GoodsReceiptNoteDetailSerializer(serializers.ModelSerializer):
    items = GoodsReceiptItemSerializer(many=True, read_only=True)
    inspection = serializers.PrimaryKeyRelatedField(read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    po_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)

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
    college_name = serializers.CharField(source='college.name', read_only=True)
    grn_number = serializers.CharField(source='grn.grn_number', read_only=True)
    inspected_by_name = serializers.CharField(source='inspected_by.get_full_name', read_only=True)

    class Meta:
        model = InspectionNote
        fields = '__all__'


class IndentItemSerializer(serializers.ModelSerializer):
    available_stock_in_central = serializers.SerializerMethodField()
    item_name = serializers.CharField(source='item.name', read_only=True)
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

    class Meta:
        model = StoreIndent
        fields = ['id', 'indent_number', 'college', 'college_name', 'status', 'priority', 'indent_date']


class StoreIndentDetailSerializer(serializers.ModelSerializer):
    items = IndentItemSerializer(many=True, read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)

    class Meta:
        model = StoreIndent
        fields = '__all__'


class StoreIndentCreateSerializer(serializers.ModelSerializer):
    items = IndentItemCreateSerializer(many=True)

    class Meta:
        model = StoreIndent
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        indent = StoreIndent.objects.create(**validated_data)
        for item_data in items_data:
            IndentItem.objects.create(indent=indent, **item_data)
        return indent


class MaterialIssueItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = MaterialIssueItem
        fields = '__all__'


class MaterialIssueItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialIssueItem
        exclude = ['material_issue']


class MaterialIssueNoteListSerializer(serializers.ModelSerializer):
    indent_number = serializers.CharField(source='indent.indent_number', read_only=True)

    class Meta:
        model = MaterialIssueNote
        fields = ['id', 'min_number', 'indent', 'indent_number', 'status', 'issue_date']


class MaterialIssueNoteDetailSerializer(serializers.ModelSerializer):
    items = MaterialIssueItemSerializer(many=True, read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    indent_number = serializers.CharField(source='indent.indent_number', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.get_full_name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.get_full_name', read_only=True)

    class Meta:
        model = MaterialIssueNote
        fields = '__all__'


class MaterialIssueNoteCreateSerializer(serializers.ModelSerializer):
    items = MaterialIssueItemCreateSerializer(many=True, required=False)

    class Meta:
        model = MaterialIssueNote
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        min_note = MaterialIssueNote.objects.create(**validated_data)
        for item_data in items_data:
            MaterialIssueItem.objects.create(material_issue=min_note, **item_data)
        return min_note


class CentralStoreInventorySerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=StoreItem.objects.none())
    central_store = serializers.PrimaryKeyRelatedField(queryset=CentralStore.objects.none())
    item_name = serializers.CharField(source='item.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)

    class Meta:
        model = CentralStoreInventory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import StoreItem, CentralStore
        # Allow items from any college that are managed centrally
        self.fields['item'].queryset = StoreItem.objects.all_colleges().filter(managed_by='central')
        # Allow any central store
        self.fields['central_store'].queryset = CentralStore.objects.all()


class InventoryTransactionSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    central_store_name = serializers.CharField(source='central_store.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = '__all__'


class StockSummarySerializer(serializers.Serializer):
    central_store = serializers.IntegerField()
    total_items = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
