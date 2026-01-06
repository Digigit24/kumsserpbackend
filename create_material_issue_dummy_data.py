"""
Create dummy material issue data for college_id=3
Run: python manage.py shell < create_material_issue_dummy_data.py
"""
from apps.core.models import College
from apps.store.models import CentralStore, StoreIndent, MaterialIssueNote
from apps.accounts.models import User
from datetime import date

# Get or create college
college, _ = College.objects.get_or_create(
    id=3,
    defaults={
        'name': 'Test College 3',
        'short_name': 'TC3',
        'code': 'TC003',
        'is_active': True
    }
)

# Get or create central store
central_store, _ = CentralStore.objects.get_or_create(
    id=6,
    defaults={
        'name': 'Main Central Store',
        'code': 'CS001',
        'address_line1': '123 Store St',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'pincode': '400001',
        'contact_phone': '9876543210',
        'contact_email': 'store@example.com',
        'manager_id': User.objects.filter(is_superuser=True).first().id,
        'is_active': True
    }
)

# Get or create indent
indent, _ = StoreIndent.objects.get_or_create(
    id=1,
    defaults={
        'indent_number': 'IND-2026-00001',
        'college': college,
        'central_store': central_store,
        'indent_date': date.today(),
        'required_by_date': date.today(),
        'priority': 'medium',
        'justification': 'Test indent for college 3',
        'status': 'approved',
        'is_active': True
    }
)

# Create or update material issue
MaterialIssueNote.objects.update_or_create(
    id=1,
    defaults={
        'min_number': 'MIN-2026-00001',
        'indent': indent,
        'central_store': central_store,
        'receiving_college': college,
        'issue_date': date.today(),
        'transport_mode': 'Courier',
        'status': 'prepared',
        'is_active': True
    }
)

# Create more material issues
for i in range(2, 6):
    MaterialIssueNote.objects.update_or_create(
        min_number=f'MIN-2026-0000{i}',
        defaults={
            'indent': indent,
            'central_store': central_store,
            'receiving_college': college,
            'issue_date': date.today(),
            'transport_mode': 'Truck',
            'status': ['prepared', 'dispatched', 'in_transit', 'received'][i-2],
            'is_active': True
        }
    )

print("✅ Created dummy material issue data for college_id=3")
print(f"Total material issues: {MaterialIssueNote.objects.filter(receiving_college_id=3).count()}")
