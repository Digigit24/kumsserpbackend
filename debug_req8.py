import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import ProcurementRequirement, PurchaseOrder, GoodsReceiptNote, GoodsReceiptItem

def debug_requirement(req_id):
    try:
        req = ProcurementRequirement.objects.get(id=req_id)
        print(f"Requirement {req.id}: {req.requirement_number} - Status: {req.status}")
        
        pos = req.purchase_orders.all()
        print(f"Total POs: {len(pos)}")
        for po in pos:
            print(f"  PO {po.id}: {po.po_number} - Status: {po.status}")
            items = po.items.all()
            for item in items:
                print(f"    Item: {item.item_description}, Qty: {item.quantity}, Received: {item.received_quantity}, Pending: {item.pending_quantity}")
            
            grns = po.goods_receipts.all()
            print(f"    Total GRNs: {len(grns)}")
            for grn in grns:
                print(f"      GRN {grn.id}: {grn.grn_number} - Status: {grn.status}")
                for g_item in grn.items.all():
                    print(f"        GRN Item: {g_item.item_description}, Received: {g_item.received_quantity}, Accepted: {g_item.accepted_quantity}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_requirement(8)
