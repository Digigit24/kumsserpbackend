import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import ProcurementRequirement, PurchaseOrder, PurchaseOrderItem

def check_pos_and_reqs():
    for req in ProcurementRequirement.objects.filter(id__in=[3, 8]):
        print(f"\nRequirement {req.id} ({req.requirement_number}) - Status: {req.status}")
        pos = req.purchase_orders.all()
        print(f"  POs count: {pos.count()}")
        for po in pos:
            print(f"    PO {po.id} ({po.po_number}) - Status: {po.status}")
            for item in po.items.all():
                print(f"      Item: {item.item_description}, Qty: {item.quantity}, Rec: {item.received_quantity}, Pend: {item.pending_quantity}")

if __name__ == "__main__":
    check_pos_and_reqs()
