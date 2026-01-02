"""
Phase 13.1: Initial data migration for Central Store setup
Creates default CentralStore, migrates Vendor data, and sets up initial configuration
"""
from django.db import migrations
from django.utils import timezone


def create_default_central_store(apps, schema_editor):
    """Create a default CentralStore instance if none exists"""
    CentralStore = apps.get_model('store', 'CentralStore')
    User = apps.get_model('accounts', 'User')

    # Check if any central store exists
    if CentralStore.objects.exists():
        print("[Migration] Central store already exists, skipping creation")
        return

    # Try to find a superuser or first user as manager
    manager = User.objects.filter(is_superuser=True).first()
    if not manager:
        manager = User.objects.first()

    if not manager:
        print("[Migration] No users found, skipping central store creation")
        return

    # Create default central store
    central_store = CentralStore.objects.create(
        name='Main Central Store',
        code='CS001',
        address_line1='Central Store Building',
        address_line2='',
        city='Main Campus',
        state='',
        pin_code='',
        contact_phone='',
        contact_email='',
        manager=manager,
        is_active=True,
    )

    print(f"[Migration] Created default central store: {central_store.name}")


def migrate_vendors_to_suppliers(apps, schema_editor):
    """Migrate existing Vendor records to SupplierMaster if applicable"""
    Vendor = apps.get_model('store', 'Vendor')
    SupplierMaster = apps.get_model('store', 'SupplierMaster')

    # Check if Vendor model has any data
    vendors = Vendor.objects.all()
    if not vendors.exists():
        print("[Migration] No vendors to migrate")
        return

    migrated_count = 0
    for vendor in vendors:
        # Check if supplier already exists with same name
        if SupplierMaster.objects.filter(name=vendor.name).exists():
            print(f"[Migration] Supplier '{vendor.name}' already exists, skipping")
            continue

        # Create new SupplierMaster from Vendor
        try:
            supplier = SupplierMaster.objects.create(
                supplier_code=f'SUP{vendor.id:04d}',  # Generate code from vendor ID
                name=vendor.name,
                contact_person=vendor.contact_person or '',
                phone=vendor.phone or '',
                email=vendor.email or '',
                address_line1=vendor.address or '',
                address_line2='',
                city='',
                state='',
                pin_code='',
                country='India',
                gstin='',
                pan='',
                bank_name='',
                bank_account='',
                bank_ifsc='',
                payment_terms='',
                credit_period=30,
                credit_limit=0,
                supplier_type='goods',
                tax_category='gst_registered',
                rating=3,
                is_active=True,
                is_blacklisted=False,
                remarks=f'Migrated from Vendor ID: {vendor.id}',
            )
            migrated_count += 1
            print(f"[Migration] Migrated vendor '{vendor.name}' to supplier '{supplier.supplier_code}'")
        except Exception as e:
            print(f"[Migration] Failed to migrate vendor '{vendor.name}': {e}")

    print(f"[Migration] Migrated {migrated_count} vendors to suppliers")


def setup_number_sequences(apps, schema_editor):
    """
    Document number sequence setup information
    Note: Number sequences are handled dynamically by utils.generate_document_number()
    This function is for documentation purposes
    """
    print("[Migration] Number sequences will be generated automatically:")
    print("  - Procurement Requirements: REQ-YYYY-NNNNN")
    print("  - Purchase Orders: PO-YYYY-NNNNN")
    print("  - Goods Receipt Notes: GRN-YYYY-NNNNN")
    print("  - Store Indents: IND-YYYY-NNNNN")
    print("  - Material Issue Notes: MIN-YYYY-NNNNN")
    print("  - Quotations: QUO-YYYY-NNNNN")


def create_default_approvers(apps, schema_editor):
    """
    Create default approver groups if they don't exist
    Note: This is optional and depends on user/group setup
    """
    Group = apps.get_model('auth', 'Group')

    # Define default approver groups for the workflow
    default_groups = [
        ('Central Store Manager', 'Can manage central store operations'),
        ('CEO', 'Chief Executive Officer - Final approver'),
        ('Finance Manager', 'Can approve financial transactions'),
        ('College Store Manager', 'Can manage college store operations'),
    ]

    created_count = 0
    for group_name, description in default_groups:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            created_count += 1
            print(f"[Migration] Created approver group: {group_name}")

    if created_count > 0:
        print(f"[Migration] Created {created_count} default approver groups")
    else:
        print("[Migration] All approver groups already exist")


def reverse_migration(apps, schema_editor):
    """Reverse migration - not fully implemented as data migration reversal can be complex"""
    print("[Migration] Reverse migration not implemented for data setup")
    print("[Migration] Manual cleanup may be required if reverting this migration")


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_centralstoreinventory_goodsreceiptitem_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_central_store, reverse_migration),
        migrations.RunPython(migrate_vendors_to_suppliers, reverse_migration),
        migrations.RunPython(setup_number_sequences, reverse_migration),
        migrations.RunPython(create_default_approvers, reverse_migration),
    ]
