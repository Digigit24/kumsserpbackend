import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import PurchaseOrder

def trigger_fulfillment():
    # Trigger check for all POs that are not yet fulfilled but should be
    for po in PurchaseOrder.objects.exclude(status='fulfilled'):
        print(f"Checking PO {po.id} ({po.po_number})...")
        po.check_fulfillment_status()
        print(f"  New Status: {po.status}")
        if po.requirement:
            print(f"  Requirement Status: {po.requirement.status}")

if __name__ == "__main__":
    trigger_fulfillment()
