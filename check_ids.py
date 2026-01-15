import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import StoreItem, CentralStoreInventory

def check_ids(target_id):
    try:
        si_exists = StoreItem.objects.filter(id=target_id).exists()
        csi_exists = CentralStoreInventory.objects.filter(id=target_id).exists()
        
        print(f"ID {target_id} exists in StoreItem: {si_exists}")
        print(f"ID {target_id} exists in CentralStoreInventory: {csi_exists}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_ids(34)
