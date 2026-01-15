import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import GoodsReceiptNote, PurchaseOrder, ProcurementRequirement

def debug_grn_fulfillment(grn_id):
    try:
        grn = GoodsReceiptNote.objects.get(id=grn_id)
        print(f"GRN {grn.id}: {grn.grn_number} - Status: {grn.status}")
        
        po = grn.purchase_order
        if not po:
            print("  No PO linked to this GRN")
            return
            
        print(f"PO {po.id}: {po.po_number} - Status: {po.status}")
        for item in po.items.all():
            print(f"  PO Item: {item.item_description}, Qty: {item.quantity}, Received: {item.received_quantity}, Pending: {item.pending_quantity}")
            
        req = po.requirement
        if req:
            print(f"Requirement {req.id}: {req.requirement_number} - Status: {req.status}")
            all_pos = req.purchase_orders.all()
            print(f"  Total POs for this requirement: {all_pos.count()}")
            for p in all_pos:
                print(f"    PO {p.id}: {p.status}")
        else:
            print("  No Requirement linked to this PO")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_grn_fulfillment(5)
