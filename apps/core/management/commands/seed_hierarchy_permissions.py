"""Seed default hierarchy-specific permissions (for org management only)."""
from django.core.management.base import BaseCommand
from apps.core.models import HierarchyPermission


class Command(BaseCommand):
    help = 'Seed hierarchy-specific permissions for organizational management'

    def handle(self, *args, **options):
        """
        These permissions are ONLY for managing the organizational hierarchy itself.
        Regular app permissions (students, fees, etc.) are handled by the existing Permission system.
        """
        permissions = [
            # Organization Management
            {'code': 'organization.view_structure', 'name': 'View Organization Structure', 'app_label': 'core', 'resource': 'organization', 'action': 'view', 'category': 'Organization'},
            {'code': 'organization.manage_structure', 'name': 'Manage Organization Structure', 'app_label': 'core', 'resource': 'organization', 'action': 'update', 'category': 'Organization'},
            {'code': 'organization.create_node', 'name': 'Create Organization Node', 'app_label': 'core', 'resource': 'node', 'action': 'create', 'category': 'Organization'},
            {'code': 'organization.delete_node', 'name': 'Delete Organization Node', 'app_label': 'core', 'resource': 'node', 'action': 'delete', 'category': 'Organization'},

            # Role Management
            {'code': 'roles.view', 'name': 'View Roles', 'app_label': 'core', 'resource': 'role', 'action': 'view', 'category': 'Role Management'},
            {'code': 'roles.create', 'name': 'Create Roles', 'app_label': 'core', 'resource': 'role', 'action': 'create', 'category': 'Role Management'},
            {'code': 'roles.update', 'name': 'Update Roles', 'app_label': 'core', 'resource': 'role', 'action': 'update', 'category': 'Role Management'},
            {'code': 'roles.delete', 'name': 'Delete Roles', 'app_label': 'core', 'resource': 'role', 'action': 'delete', 'category': 'Role Management'},
            {'code': 'roles.assign_to_users', 'name': 'Assign Roles to Users', 'app_label': 'core', 'resource': 'role', 'action': 'update', 'category': 'Role Management'},

            # Permission Management
            {'code': 'permissions.view', 'name': 'View Permissions', 'app_label': 'core', 'resource': 'permission', 'action': 'view', 'category': 'Permission Management'},
            {'code': 'permissions.assign_to_roles', 'name': 'Assign Permissions to Roles', 'app_label': 'core', 'resource': 'permission', 'action': 'update', 'category': 'Permission Management'},

            # Team Management
            {'code': 'teams.view', 'name': 'View Teams', 'app_label': 'core', 'resource': 'team', 'action': 'view', 'category': 'Team Management'},
            {'code': 'teams.manage', 'name': 'Manage Teams', 'app_label': 'core', 'resource': 'team', 'action': 'update', 'category': 'Team Management'},
            {'code': 'teams.add_members', 'name': 'Add Team Members', 'app_label': 'core', 'resource': 'team', 'action': 'update', 'category': 'Team Management'},

            # System Admin
            {'code': 'system.manage_users', 'name': 'Manage User Accounts', 'app_label': 'accounts', 'resource': 'user', 'action': 'update', 'category': 'System Administration'},
            {'code': 'system.view_audit_logs', 'name': 'View Audit Logs', 'app_label': 'core', 'resource': 'audit', 'action': 'view', 'category': 'System Administration'},
        ]

        created_count = 0
        for perm_data in permissions:
            perm, created = HierarchyPermission.objects.get_or_create(
                code=perm_data['code'],
                defaults=perm_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created permission: {perm.code}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully seeded {created_count} hierarchy permissions'))
        self.stdout.write(self.style.WARNING('\nNote: These permissions are for org hierarchy management only.'))
        self.stdout.write(self.style.WARNING('Regular app permissions (students, fees, etc.) use the existing Permission system.'))
