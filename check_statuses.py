import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import GoodsReceiptNote, PurchaseOrder, ProcurementRequirement

def print_final_statuses():
    print("--- GRNs ---")
    for grn in GoodsReceiptNote.objects.all():
        print(f"GRN {grn.id} ({grn.grn_number}): {grn.status} (Linked PO: {grn.purchase_order_id})")
        
    print("\n--- POs ---")
    for po in PurchaseOrder.objects.all():
        print(f"PO {po.id} ({po.po_number}): {po.status} (Linked Req: {po.requirement_id})")
        for item in po.items.all():
            print(f"  Item: {item.item_description}, Qty: {item.quantity}, Received: {item.received_quantity}")

    print("\n--- Requirements ---")
    for req in ProcurementRequirement.objects.all():
        print(f"Req {req.id} ({req.requirement_number}): {req.status}")

if __name__ == "__main__":
    print_final_statuses()
