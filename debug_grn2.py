import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import GoodsReceiptNote

def debug_grn(grn_id):
    try:
        grn = GoodsReceiptNote.objects.get(id=grn_id)
        print(f"GRN {grn.id}: {grn.grn_number} - Status: {grn.status}")
        if grn.purchase_order:
            print(f"  Linked to PO: {grn.purchase_order.id} ({grn.purchase_order.po_number})")
            if grn.purchase_order.requirement:
                print(f"  Linked to Requirement: {grn.purchase_order.requirement.id}")
        else:
            print("  No linked PO")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_grn(2)
