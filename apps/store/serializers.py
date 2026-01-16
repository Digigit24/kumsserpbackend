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
        fields = '__all__'
        extra_kwargs = {'quotation': {'required': False}}


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
                  'quotation_date', 'supplier_reference_number', 'valid_until', 'total_amount', 'tax_amount',
                  'grand_total', 'payment_terms', 'delivery_time_days', 'warranty_terms',
                  'status', 'is_selected', 'quotation_file_url']


class SupplierQuotationDetailSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    supplier_details = SupplierMasterDetailSerializer(source='supplier', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    requirement_number = serializers.CharField(source='requirement.requirement_number', read_only=True)
    requirement_title = serializers.CharField(source='requirement.title', read_only=True)
    item_description = serializers.CharField(source='requirement.item_description', read_only=True)
    quantity = serializers.IntegerField(source='requirement.quantity', read_only=True)
    unit = serializers.CharField(source='requirement.unit', read_only=True)
    estimated_unit_price = serializers.DecimalField(source='requirement.estimated_unit_price', max_digits=12, decimal_places=2, read_only=True)
    estimated_total = serializers.DecimalField(source='requirement.estimated_total', max_digits=12, decimal_places=2, read_only=True)
    specifications = serializers.CharField(source='requirement.specifications', read_only=True)
    quotation_file_url = serializers.SerializerMethodField()

    class Meta:
        model = SupplierQuotation
        fields = '__all__'

    def get_quotation_file_url(self, obj):
        if not obj.quotation_file:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.quotation_file.url) if request else obj.quotation_file.url

    def validate_quotation_file(self, value):
        return _validate_quotation_file(value)


class SupplierQuotationCreateSerializer(serializers.ModelSerializer):
    requirement = serializers.PrimaryKeyRelatedField(queryset=ProcurementRequirement.objects.all(), required=False, allow_null=True)
    quotation_date = serializers.DateField(required=False, allow_null=True)
    valid_until = serializers.DateField(required=False, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    grand_total = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    supplier = serializers.PrimaryKeyRelatedField(queryset=SupplierMaster.objects.all(), required=False, allow_null=True)
    items = QuotationItemCreateSerializer(many=True, required=False)

    class Meta:
        model = SupplierQuotation
        fields = '__all__'
        read_only_fields = ['quotation_number', 'status', 'is_selected']

    def validate_quotation_file(self, value):
        return _validate_quotation_file(value)

    def to_representation(self, instance):
        # Use DetailSerializer for full response after creation
        return SupplierQuotationDetailSerializer(instance, context=self.context).data

    def create(self, validated_data):
        if not validated_data.get('quotation_date'):
            validated_data['quotation_date'] = timezone.now().date()
        if not validated_data.get('valid_until'):
            validated_data['valid_until'] = validated_data['quotation_date']
        
        # Ensure new quotations are active by default
        validated_data['is_active'] = True

        total_amount = validated_data.get('total_amount')
        tax_amount = validated_data.get('tax_amount')
        grand_total = validated_data.get('grand_total')

        if total_amount is None:
            validated_data['total_amount'] = 0
        if tax_amount is None:
            validated_data['tax_amount'] = 0
        if grand_total is None:
            validated_data['grand_total'] = (validated_data.get('total_amount') or 0) + (validated_data.get('tax_amount') or 0)

        if not validated_data.get('requirement'):
            requirement = ProcurementRequirement.objects.filter(status='approved').first()
            if not requirement:
                requirement = ProcurementRequirement.objects.first()
            if not requirement:
                raise serializers.ValidationError({'requirement': 'No procurement requirement available. Create one first.'})
            validated_data['requirement'] = requirement

        if not validated_data.get('supplier'):
            supplier = SupplierMaster.objects.filter(is_active=True).first()
            if not supplier:
                raise serializers.ValidationError({'supplier': 'No active supplier available to use as default.'})
            validated_data['supplier'] = supplier

        items_data = validated_data.pop('items', [])
        
        # If items provided, calculate totals if they are zero/None
        if items_data:
            calc_total = 0
            calc_tax = 0
            for item in items_data:
                qty = item.get('quantity', 0)
                price = item.get('unit_price', 0)
                tax_rate = item.get('tax_rate', 0)
                
                line_total = qty * price
                line_tax = (line_total * tax_rate) / 100
                
                item['total_amount'] = line_total + line_tax
                item['tax_amount'] = line_tax
                
                calc_total += line_total
                calc_tax += line_tax
                
                # Attempt to find requirement_item by description if not provided
                if not item.get('requirement_item') and validated_data.get('requirement'):
                    from .models import RequirementItem
                    match = RequirementItem.objects.filter(
                        requirement=validated_data['requirement'],
                        item_description__iexact=item.get('item_description')
                    ).first()
                    if match:
                        item['requirement_item'] = match.id

            if not validated_data.get('total_amount'):
                validated_data['total_amount'] = calc_total
            if not validated_data.get('tax_amount'):
                validated_data['tax_amount'] = calc_tax
            if not validated_data.get('grand_total'):
                validated_data['grand_total'] = calc_total + calc_tax

        quotation = super().create(validated_data)
        
        # Create items
        for item_data in items_data:
            QuotationItem.objects.create(quotation=quotation, **item_data)
        
        # Update requirement status to 'quotations_received'
        requirement = quotation.requirement
        if requirement and requirement.status == 'approved':
            requirement.status = 'quotations_received'
            requirement.save(update_fields=['status', 'updated_at'])
            
        return quotation


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

    items = QuotationItemCreateSerializer(many=True, required=False)

    def to_representation(self, instance):
        return SupplierQuotationDetailSerializer(instance, context=self.context).data

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        # If items are provided, handles recalculation of totals if they are not explicitly updated
        if items_data is not None:
            calc_total = 0
            calc_tax = 0
            requirement = validated_data.get('requirement', instance.requirement)

            for item in items_data:
                qty = item.get('quantity', 0)
                price = item.get('unit_price', 0)
                tax_rate = item.get('tax_rate', 0)
                
                line_total = qty * price
                line_tax = (line_total * tax_rate) / 100
                
                item['total_amount'] = line_total + line_tax
                item['tax_amount'] = line_tax
                
                calc_total += line_total
                calc_tax += line_tax
                
                # Auto-link requirement item
                if not item.get('requirement_item') and requirement:
                    from .models import RequirementItem
                    match = RequirementItem.objects.filter(
                        requirement=requirement,
                        item_description__iexact=item.get('item_description')
                    ).first()
                    if match:
                        item['requirement_item'] = match

            if 'total_amount' not in validated_data:
                validated_data['total_amount'] = calc_total
            if 'tax_amount' not in validated_data:
                validated_data['tax_amount'] = calc_tax
            if 'grand_total' not in validated_data:
                validated_data['grand_total'] = calc_total + calc_tax

        instance = super().update(instance, validated_data)
        
        if items_data is not None:
            # Simple replacement logic for items
            instance.items.all().delete()
            for item_data in items_data:
                QuotationItem.objects.create(quotation=instance, **item_data)
                
        return instance

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
    
    # Make fields optional for input as we'll pull them from requirement/quotation
    supplier = serializers.PrimaryKeyRelatedField(queryset=SupplierMaster.objects.all(), required=False)
    central_store = serializers.PrimaryKeyRelatedField(queryset=CentralStore.objects.all(), required=False)
    po_date = serializers.DateField(required=False)
    expected_delivery_date = serializers.DateField(required=False)
    delivery_address_line1 = serializers.CharField(required=False)
    delivery_city = serializers.CharField(required=False)
    delivery_state = serializers.CharField(required=False)
    delivery_pincode = serializers.CharField(required=False)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    tax_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    payment_terms = serializers.CharField(required=False)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        requirement = validated_data.get('requirement')
        quotation = validated_data.get('quotation')
        
        # Automatically populate fields from requirement and quotation if not provided
        if not validated_data.get('supplier') and quotation:
            validated_data['supplier'] = quotation.supplier
            
        if not validated_data.get('central_store') and requirement:
            validated_data['central_store'] = requirement.central_store
            
        if not validated_data.get('po_date'):
            validated_data['po_date'] = timezone.now().date()
            
        if not validated_data.get('expected_delivery_date'):
            if quotation and quotation.delivery_time_days:
                validated_data['expected_delivery_date'] = validated_data['po_date'] + timezone.timedelta(days=quotation.delivery_time_days)
            else:
                validated_data['expected_delivery_date'] = validated_data['po_date'] + timezone.timedelta(days=7)
                
        # Use central store address if delivery address is missing
        cs = validated_data.get('central_store')
        if cs:
            if not validated_data.get('delivery_address_line1'):
                validated_data['delivery_address_line1'] = cs.address_line1
            if not validated_data.get('delivery_city'):
                validated_data['delivery_city'] = cs.city
            if not validated_data.get('delivery_state'):
                validated_data['delivery_state'] = cs.state
            if not validated_data.get('delivery_pincode'):
                validated_data['delivery_pincode'] = cs.pincode
                
        if not validated_data.get('total_amount') and quotation:
            validated_data['total_amount'] = quotation.total_amount
            
        if not validated_data.get('tax_amount') and quotation:
            validated_data['tax_amount'] = quotation.tax_amount
            
        if not validated_data.get('payment_terms'):
            if quotation and quotation.payment_terms:
                validated_data['payment_terms'] = quotation.payment_terms
            else:
                validated_data['payment_terms'] = 'Standard'

        po = PurchaseOrder.objects.create(**validated_data)
        
        # If no items provided, copy items from quotation
        if not items_data and quotation:
            for q_item in quotation.items.all():
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    quotation_item=q_item,
                    item_description=q_item.item_description,
                    hsn_code=q_item.hsn_code,
                    quantity=q_item.quantity,
                    unit=q_item.unit,
                    unit_price=q_item.unit_price,
                    tax_rate=q_item.tax_rate,
                    tax_amount=q_item.tax_amount,
                    total_amount=q_item.total_amount,
                    specifications=q_item.specifications
                )
        else:
            for item_data in items_data:
                PurchaseOrderItem.objects.create(purchase_order=po, **item_data)
        
        # Update requirement status
        if requirement:
            requirement.status = 'po_created'
            requirement.save(update_fields=['status', 'updated_at'])
            
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
        extra_kwargs = {
            'po_item': {'required': False, 'allow_null': True},
            'item_description': {'required': False, 'allow_null': True},
            'ordered_quantity': {'required': False, 'allow_null': True},
            'received_quantity': {'required': False, 'allow_null': True},
            'unit': {'required': False, 'allow_null': True},
        }


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
        extra_kwargs = {
            'purchase_order': {'required': False, 'allow_null': True},
            'supplier': {'required': False, 'allow_null': True},
            'central_store': {'required': False, 'allow_null': True},
            'receipt_date': {'required': False, 'allow_null': True},
            'invoice_number': {'required': False, 'allow_null': True},
            'invoice_date': {'required': False, 'allow_null': True},
            'invoice_amount': {'required': False, 'allow_null': True},
        }


class GoodsReceiptNoteCreateSerializer(serializers.ModelSerializer):
    items = GoodsReceiptItemCreateSerializer(many=True, required=False)

    class Meta:
        model = GoodsReceiptNote
        fields = '__all__'
        extra_kwargs = {
            'purchase_order': {'required': False, 'allow_null': True},
            'supplier': {'required': False, 'allow_null': True},
            'central_store': {'required': False, 'allow_null': True},
            'receipt_date': {'required': False, 'allow_null': True},
            'invoice_number': {'required': False, 'allow_null': True},
            'invoice_date': {'required': False, 'allow_null': True},
            'invoice_amount': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        po = validated_data.get('purchase_order')
        
        # Pull defaults from PO if provided
        if po:
            validated_data.setdefault('supplier', po.supplier)
            validated_data.setdefault('central_store', po.central_store)
            validated_data.setdefault('invoice_amount', po.grand_total)
            if not validated_data.get('invoice_number'):
                validated_data['invoice_number'] = f"INV-{po.po_number}"
        
        # Set absolute defaults for required model fields
        validated_data.setdefault('receipt_date', timezone.now().date())
        validated_data.setdefault('invoice_date', timezone.now().date())
        if not validated_data.get('invoice_number'):
            validated_data['invoice_number'] = f"INV-{timezone.now().strftime('%Y%m%d%H%M')}"
        validated_data.setdefault('invoice_amount', 0)

        grn = GoodsReceiptNote.objects.create(**validated_data)
        
        # Handle linked items
        if not items_data and po:
            for po_item in po.items.all():
                GoodsReceiptItem.objects.create(
                    grn=grn,
                    po_item=po_item,
                    item_description=po_item.item_description,
                    ordered_quantity=po_item.quantity,
                    received_quantity=po_item.quantity,
                    accepted_quantity=po_item.quantity,
                    unit=po_item.unit
                )
        else:
            for item_data in items_data:
                poi = item_data.get('po_item')
                if poi:
                    item_data.setdefault('item_description', poi.item_description)
                    item_data.setdefault('ordered_quantity', poi.quantity)
                    item_data.setdefault('received_quantity', poi.quantity)
                    item_data.setdefault('unit', poi.unit)
                
                # Model-level required fallbacks
                item_data.setdefault('item_description', 'Goods Receipt Item')
                item_data.setdefault('unit', 'Unit')
                item_data.setdefault('ordered_quantity', 0)
                item_data.setdefault('received_quantity', 0)
                
                # Satisfy model clean requirements
                received = item_data.get('received_quantity', 0)
                if received > 0 and not item_data.get('accepted_quantity') and not item_data.get('rejected_quantity'):
                    item_data['accepted_quantity'] = received
                
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
    # Accept CentralStoreInventory ID (what frontend sends) and resolve to StoreItem
    central_store_item = serializers.IntegerField()

    class Meta:
        model = IndentItem
        exclude = ['indent']

    def validate_central_store_item(self, value):
        """Convert CentralStoreInventory ID to StoreItem instance."""
        from .models import CentralStoreInventory, StoreItem
        
        # First try to find by CentralStoreInventory ID
        inventory = CentralStoreInventory.objects.filter(id=value).first()
        if inventory and inventory.item:
            return inventory.item
        
        # Fallback: check if it's a direct StoreItem ID
        item = StoreItem._base_manager.filter(id=value).first()
        if item:
            return item
        
        raise serializers.ValidationError(f"Invalid item ID {value} - not found in inventory or items.")



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
    """For GET - returns inventory ID and item details"""
    item_display = serializers.SerializerMethodField()
    central_store_name = serializers.SerializerMethodField()

    class Meta:
        model = CentralStoreInventory
        fields = ['id', 'item', 'item_display', 'central_store', 'central_store_name',
                  'quantity_on_hand', 'quantity_allocated', 'quantity_available',
                  'min_stock_level', 'reorder_point', 'max_stock_level',
                  'last_stock_update', 'unit_cost', 'is_active',
                  'created_at', 'updated_at']

    def get_item_display(self, obj):
        try:
            # Use _base_manager to bypass filtering
            from .models import StoreItem
            item = StoreItem._base_manager.filter(id=obj.item_id).first()
            return item.name if item else 'Unknown'
        except:
            return 'Unknown'

    def get_central_store_name(self, obj):
        try:
            return obj.central_store.name
        except:
            return 'Unknown'


class CentralStoreInventoryCreateSerializer(serializers.ModelSerializer):
    """For POST - only accepts item_name"""
    item_name = serializers.CharField(write_only=True)

    class Meta:
        model = CentralStoreInventory
        fields = ['item_name', 'central_store', 'quantity_on_hand',
                  'quantity_allocated', 'quantity_available', 'min_stock_level',
                  'reorder_point', 'max_stock_level', 'unit_cost', 'is_active']
        read_only_fields = ['quantity_available']

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
        from .models import StoreItem, StoreCategory, CentralStore
        from django.db import transaction
        import logging
        logger = logging.getLogger(__name__)

        try:
            item_name = validated_data.pop('item_name')
            central_store = validated_data.get('central_store')

            if not central_store:
                raise serializers.ValidationError({'central_store': 'Required'})

            with transaction.atomic():
                # Central stores are not college-specific, use first college or None
                from apps.core.models import College
                college = College.objects.first()
                college_id = college.id if college else None

                # Find or create item for central management
                item = StoreItem._base_manager.filter(
                    name__iexact=item_name,
                    managed_by='central'
                ).first()

                if not item:
                    # Get or create category
                    category = StoreCategory._base_manager.filter(
                        name='General',
                        college_id=college_id
                    ).first()

                    if not category and college_id:
                        category = StoreCategory._base_manager.create(
                            name='General',
                            code='GEN',
                            college_id=college_id,
                            is_active=True
                        )

                    # Create item
                    if college_id and category:
                        item = StoreItem._base_manager.create(
                            name=item_name,
                            code=item_name.upper().replace(' ', '_')[:20],
                            category=category,
                            unit='unit',
                            price=0,
                            managed_by='central',
                            college_id=college_id,
                            is_active=True
                        )
                    else:
                        raise serializers.ValidationError({'error': 'No college found. Create a college first.'})

                # Create inventory
                inventory = CentralStoreInventory._base_manager.create(
                    central_store=central_store,
                    item=item,
                    quantity_on_hand=validated_data.get('quantity_on_hand', 0),
                    quantity_allocated=validated_data.get('quantity_allocated', 0),
                    quantity_available=validated_data.get('quantity_on_hand', 0) - validated_data.get('quantity_allocated', 0),
                    min_stock_level=validated_data.get('min_stock_level', 0),
                    reorder_point=validated_data.get('reorder_point', 0),
                    max_stock_level=validated_data.get('max_stock_level'),
                    unit_cost=validated_data.get('unit_cost', 0),
                    is_active=validated_data.get('is_active', True),
                    created_by=self.context['request'].user,
                    updated_by=self.context['request'].user
                )

                return inventory

        except serializers.ValidationError:
            raise
        except Exception as e:
            logger.error(f"Inventory creation error: {str(e)}", exc_info=True)
            raise serializers.ValidationError({'error': str(e)})

    def to_representation(self, instance):
        """Return full representation using list serializer"""
        return CentralStoreInventoryListSerializer(instance, context=self.context).data


class CentralStoreInventorySerializer(CentralStoreInventoryListSerializer):
    """Default - same as list"""

    class Meta(CentralStoreInventoryListSerializer.Meta):
        read_only_fields = ['quantity_available']

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
