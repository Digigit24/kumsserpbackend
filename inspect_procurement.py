import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote

def inspect_pos():
    for po in PurchaseOrder.objects.all():
        print(f"\nPO {po.id} ({po.po_number}) - Status: {po.status}")
        items = po.items.all()
        print(f"  Items count: {items.count()}")
        for item in items:
            print(f"    Item: {item.item_description}")
            print(f"      Ordered: {item.quantity}")
            print(f"      Received: {item.received_quantity}")
            print(f"      Pending: {item.pending_quantity}")
            
        grns = po.goods_receipts.all()
        print(f"  GRNs count: {grns.count()}")
        for grn in grns:
            print(f"    GRN {grn.id} ({grn.grn_number}) - Status: {grn.status}")
            for g_item in grn.items.all():
                 print(f"      GRN Item: {g_item.item_description}, Accepted: {g_item.accepted_quantity}")

if __name__ == "__main__":
    inspect_pos()
