import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.core.models import College
from apps.store.models import (
    CentralStore, StoreCategory, StoreItem, StoreIndent, 
    IndentItem, MaterialIssueNote, MaterialIssueItem, CentralStoreInventory
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed dummy data for Material Issue Notes with different statuses'

    def handle(self, *args, **options):
        self.stdout.write('Seeding material issue dummy data...')

        # 1. Get or create a superuser for management
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin_dummy',
                email='admin@example.com',
                password='password123'
            )
            self.stdout.write(f'Created superuser: {admin_user.username}')

        # 2. Get or create Central Store
        central_store, created = CentralStore.objects.get_or_create(
            code='CS001',
            defaults={
                'name': 'Main University Central Store',
                'address_line1': '123 University Road',
                'city': 'Metropolis',
                'state': 'Central State',
                'pincode': '123456',
                'manager': admin_user,
                'contact_phone': '9876543210',
                'contact_email': 'centralstore@university.edu'
            }
        )
        if created:
            self.stdout.write(f'Created Central Store: {central_store.name}')

        # 3. Get or create a College
        college = College.objects.filter(is_active=True).exclude(id=1).first()
        if not college:
            college = College.objects.create(
                code='COL001',
                name='Engineering College Branch 1',
                short_name='ECB1',
                email='contact@ecb1.edu',
                phone='011-22334455',
                address_line1='Engineering Block, Campus North',
                city='Metropolis',
                state='Central State',
                pincode='123456'
            )
            self.stdout.write(f'Created College: {college.name}')

        # 4. Create Store Category and Items
        category, _ = StoreCategory.objects.all_colleges().get_or_create(
            college_id=1,
            code='GEN',
            defaults={'name': 'General Supplies'}
        )

        items_data = [
            {'name': 'A4 Paper Bundle', 'code': 'PAP-A4', 'unit': 'bundle'},
            {'name': 'Black Ink Pen', 'code': 'PEN-BLK', 'unit': 'box'},
            {'name': 'Stapler', 'code': 'STP-01', 'unit': 'piece'},
            {'name': 'Whiteboard Marker', 'code': 'MRK-WHT', 'unit': 'set'},
        ]

        items = []
        for item_info in items_data:
            item, created = StoreItem.objects.all_colleges().get_or_create(
                college_id=1,
                code=item_info['code'],
                defaults={
                    'name': item_info['name'],
                    'category': category,
                    'unit': item_info['unit'],
                    'managed_by': 'central',
                    'price': 0,
                    'min_stock_level': 10
                }
            )
            items.append(item)
            
            # Ensure stock in central inventory
            inventory, _ = CentralStoreInventory.objects.get_or_create(
                central_store=central_store,
                item=item,
                defaults={
                    'quantity_on_hand': 1000,
                    'quantity_available': 1000,
                    'unit_cost': 50.00
                }
            )

        # 5. Define Statuses for Indents and MINs
        # MIN Statuses: prepared, dispatched, in_transit, received, cancelled
        statuses = ['prepared', 'dispatched', 'in_transit', 'received', 'cancelled']
        
        for idx, status in enumerate(statuses):
            # Create an approved indent for each status
            indent = StoreIndent.objects.create(
                college=college,
                central_store=central_store,
                requesting_store_manager=admin_user,
                required_by_date=date.today() + timedelta(days=7),
                priority='medium',
                justification=f'Replacement supplies for {status} test case',
                status='super_admin_approved',
                approved_by=admin_user,
                approved_date=timezone.now()
            )

            # Add 2 items to indent
            indent_items = []
            selected_items = random.sample(items, 2)
            for s_item in selected_items:
                ii = IndentItem.objects.create(
                    indent=indent,
                    central_store_item=s_item,
                    requested_quantity=20,
                    approved_quantity=20,
                    unit=s_item.unit
                )
                indent_items.append(ii)

            # Create Material Issue Note
            min_note = MaterialIssueNote.objects.create(
                indent=indent,
                central_store=central_store,
                receiving_college=college,
                issue_date=date.today() - timedelta(days=idx),
                issued_by=admin_user,
                status=status,
                transport_mode='Courier' if status != 'cancelled' else None,
                vehicle_number=f'UP-16-AB-{1000+idx}' if status in ['dispatched', 'in_transit', 'received'] else None,
                dispatch_date=timezone.now() - timedelta(hours=idx*2) if status in ['dispatched', 'in_transit', 'received'] else None,
                receipt_date=timezone.now() if status == 'received' else None,
                received_by=admin_user if status == 'received' else None
            )

            # Create items for MIN
            for ii in indent_items:
                MaterialIssueItem.objects.create(
                    material_issue=min_note,
                    indent_item=ii,
                    item=ii.central_store_item,
                    issued_quantity=ii.approved_quantity,
                    unit=ii.unit,
                    batch_number=f'BATCH-{random.randint(100, 999)}'
                )
                
                # Update indent item issued quantity if status is at least dispatched
                if status in ['dispatched', 'in_transit', 'received']:
                    ii.update_issued_quantity(ii.approved_quantity)

            self.stdout.write(self.style.SUCCESS(f'✓ Created MIN {min_note.min_number} with status: {status}'))

        self.stdout.write(self.style.SUCCESS('\nFinished seeding material issue dummy data!'))
