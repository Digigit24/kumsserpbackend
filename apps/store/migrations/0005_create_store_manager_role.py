"""
Migration to create Store Manager role with appropriate permissions.
This role can manage store indents, view inventory, and handle material issues.
"""
from django.db import migrations


def create_store_manager_role(apps, schema_editor):
    """Create Store Manager role for each college."""
    College = apps.get_model('core', 'College')
    Role = apps.get_model('accounts', 'Role')

    # Store manager permissions
    store_permissions = {
        'store': {
            'view': True,
            'create': True,
            'edit': True,
            'delete': False,  # Can't delete store records
        },
        'store_indent': {
            'view': True,
            'create': True,
            'edit': True,
            'delete': False,
            'submit': True,  # Can submit indents for approval
        },
        'material_issue': {
            'view': True,
            'confirm_receipt': True,  # Can confirm receipt of materials
        },
        'inventory': {
            'view': True,
            'view_reports': True,
        },
        'approvals': {
            'view': True,
            'create': True,
        }
    }

    for college in College.objects.all():
        Role.objects.get_or_create(
            college=college,
            code='store_manager',
            defaults={
                'name': 'Store Manager',
                'description': 'Manages college store operations, creates indents, and handles material receipts',
                'permissions': store_permissions,
                'is_active': True,
                'display_order': 50,
            }
        )


def reverse_create_role(apps, schema_editor):
    """Remove Store Manager role."""
    Role = apps.get_model('accounts', 'Role')
    Role.objects.filter(code='store_manager').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_goodsreceiptnote_delivery_challan_file_and_more'),
        ('accounts', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_store_manager_role, reverse_create_role),
    ]
