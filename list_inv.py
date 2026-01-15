import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import CentralStoreInventory

def list_inventory():
    try:
        print("Last 20 items in CentralStoreInventory:")
        for i in CentralStoreInventory._base_manager.all().order_by('-id')[:20]:
            print(f"ID: {i.id}, Item: {i.item.name if i.item else 'N/A'}, is_active: {i.is_active}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_inventory()
