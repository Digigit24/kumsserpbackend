import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import CentralStoreInventory

def check_inventory(inv_id):
    try:
        inv_active = CentralStoreInventory.objects.filter(id=inv_id, is_active=True).exists()
        inv_inactive = CentralStoreInventory.objects.filter(id=inv_id, is_active=False).exists()
        inv_base = CentralStoreInventory._base_manager.filter(id=inv_id).exists()
        
        print(f"ID {inv_id} exists and is active: {inv_active}")
        print(f"ID {inv_id} exists and is inactive: {inv_inactive}")
        print(f"ID {inv_id} exists in base manager: {inv_base}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_inventory(34)
