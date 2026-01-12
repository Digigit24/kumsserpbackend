
"""
Create comprehensive dummy data for Procurement, Store Indents, and Material Issues across all statuses.
Run: python manage.py shell < create_procurement_dummy_data.py
"""
import random
from datetime import date, timedelta
from django.utils import timezone
from apps.core.models import College
from apps.store.models import (
    CentralStore, StoreIndent, MaterialIssueNote, ProcurementRequirement, 
    RequirementItem, StoreCategory, SupplierMaster, SupplierQuotation, 
    QuotationItem, PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote,
    StoreIndentItem
)
from apps.accounts.models import User

# --- Setup Foundation ---
print("--- Setting up Foundation ---")

# Ensure college exists
college, _ = College.objects.get_or_create(
    id=3,
    defaults={
        'name': 'Test College 3',
        'short_name': 'TC3',
        'code': 'TC003',
        'is_active': True
    }
)

# Ensure central store exists
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    # If no superuser, try any user
    admin_user = User.objects.first()

central_store, _ = CentralStore.objects.get_or_create(
    id=6,
    defaults={
        'name': 'Main Central Store',
        'code': 'CS001',
        'address_line1': '123 Store St',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'pincode': '400001',
        'contact_phone': '9876543210',
        'contact_email': 'store@example.com',
        'manager': admin_user,
        'is_active': True
    }
)

# Ensure some categories exist
categories = []
for cat_name, cat_code in [('Electronics', 'ELEC'), ('Stationery', 'STAT'), ('Furniture', 'FURN')]:
    cat, _ = StoreCategory.objects.get_or_create(
        college=college,
        code=cat_code,
        defaults={'name': cat_name}
    )
    categories.append(cat)

# Ensure some suppliers exist
suppliers = []
for i in range(1, 4):
    sup, _ = SupplierMaster.objects.get_or_create(
        name=f"Vendor {i}",
        defaults={
            'phone': f'900000000{i}',
            'address_line1': f'Street {i}',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'supplier_type': 'manufacturer',
            'is_active': True
        }
    )
    suppliers.append(sup)

# --- 1. Store Indents (all statuses) ---
print("--- Creating Store Indents ---")
indent_statuses = [
    'draft', 'submitted', 'pending_college_approval', 'college_approved', 
    'pending_super_admin', 'super_admin_approved', 'approved', 
    'partially_fulfilled', 'fulfilled', 'rejected', 'cancelled'
]

for status in indent_statuses:
    indent = StoreIndent.objects.create(
        indent_number=f"IND-{status.upper()[:4]}-{random.randint(1000, 9999)}",
        college=college,
        central_store=central_store,
        requesting_store_manager=admin_user,
        required_by_date=date.today() + timedelta(days=7),
        priority='medium',
        justification=f"Sample requirement for status {status}",
        status=status
    )
    # Add items
    StoreIndentItem.objects.create(
        indent=indent,
        item_name="Printer Paper",
        quantity_requested=50,
        unit="Rim"
    )

# --- 2. Procurement Requirements (all statuses) ---
print("--- Creating Procurement Requirements ---")
proc_statuses = [
    'draft', 'submitted', 'pending_approval', 'approved', 
    'quotations_received', 'po_created', 'fulfilled', 'cancelled'
]

for status in proc_statuses:
    req = ProcurementRequirement.objects.create(
        requirement_number=f"REQ-{status.upper()[:4]}-{random.randint(1000, 9999)}",
        central_store=central_store,
        title=f"Bulk Purchase for {status}",
        description=f"Detailed description for {status} procurement",
        required_by_date=date.today() + timedelta(days=30),
        urgency='high',
        status=status,
        justification="Needed for annual operations",
        estimated_budget=50000.00
    )
    
    # Add items
    ritem = RequirementItem.objects.create(
        requirement=req,
        item_description="Laptops for staff",
        quantity=5,
        estimated_unit_price=10000.00
    )
    
    # Special logic for some statuses to make them meaningful
    if status == 'quotations_received' or status == 'po_created' or status == 'fulfilled':
        # Add a quotation
        quot = SupplierQuotation.objects.create(
            quotation_number=f"QUO-{req.id}-{random.randint(100, 999)}",
            requirement=req,
            supplier=suppliers[0],
            quotation_date=date.today(),
            valid_until=date.today() + timedelta(days=15),
            total_amount=48000.00,
            status='received',
            is_selected=(status != 'quotations_received')
        )
        qitem = QuotationItem.objects.create(
            quotation=quot,
            requirement_item=ritem,
            quantity=5,
            unit_price=9600.00,
            total_price=48000.00
        )
        
        if status == 'po_created' or status == 'fulfilled':
            # Add a PO
            po = PurchaseOrder.objects.create(
                po_number=f"PO-{req.id}-{random.randint(100, 999)}",
                requirement=req,
                supplier=suppliers[0],
                central_store=central_store,
                po_date=date.today(),
                total_amount=48000.00,
                status='sent' if status == 'po_created' else 'fulfilled'
            )
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                quotation_item=qitem,
                quantity=5,
                unit_price=9600.00,
                total_price=48000.00
            )

# --- 3. Material Issue Notes (all statuses) ---
print("--- Creating Material Issues ---")
min_statuses = ['prepared', 'dispatched', 'in_transit', 'received', 'cancelled']

# Find an approved indent to link to
base_indent = StoreIndent.objects.filter(status='approved', college=college).first()

for status in min_statuses:
    MaterialIssueNote.objects.create(
        min_number=f"MIN-{status.upper()[:4]}-{random.randint(1000, 9999)}",
        indent=base_indent,
        central_store=central_store,
        receiving_college=college,
        issue_date=date.today(),
        transport_mode='Vehicle',
        vehicle_number='MH-01-AB-1234',
        status=status
    )

print("✅ Successfully created all dummy data!")
