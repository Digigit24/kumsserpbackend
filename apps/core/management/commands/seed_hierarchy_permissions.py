"""Seed default permissions for the hierarchy system."""
from django.core.management.base import BaseCommand
from apps.core.models import HierarchyPermission


class Command(BaseCommand):
    help = 'Seed default permissions for organizational hierarchy'

    def handle(self, *args, **options):
        permissions = [
            # Students
            {'code': 'students.view', 'name': 'View Students', 'app_label': 'students', 'resource': 'student', 'action': 'view', 'category': 'Academic'},
            {'code': 'students.create', 'name': 'Create Student', 'app_label': 'students', 'resource': 'student', 'action': 'create', 'category': 'Academic'},
            {'code': 'students.update', 'name': 'Update Student', 'app_label': 'students', 'resource': 'student', 'action': 'update', 'category': 'Academic'},
            {'code': 'students.delete', 'name': 'Delete Student', 'app_label': 'students', 'resource': 'student', 'action': 'delete', 'category': 'Academic'},

            # Fees
            {'code': 'fees.view', 'name': 'View Fees', 'app_label': 'fees', 'resource': 'invoice', 'action': 'view', 'category': 'Financial'},
            {'code': 'fees.create', 'name': 'Create Invoice', 'app_label': 'fees', 'resource': 'invoice', 'action': 'create', 'category': 'Financial'},
            {'code': 'fees.approve', 'name': 'Approve Invoice', 'app_label': 'fees', 'resource': 'invoice', 'action': 'approve', 'category': 'Financial'},

            # Academic
            {'code': 'academic.view', 'name': 'View Academic Data', 'app_label': 'academic', 'resource': 'class', 'action': 'view', 'category': 'Academic'},
            {'code': 'academic.create', 'name': 'Create Class', 'app_label': 'academic', 'resource': 'class', 'action': 'create', 'category': 'Academic'},
            {'code': 'academic.update', 'name': 'Update Timetable', 'app_label': 'academic', 'resource': 'timetable', 'action': 'update', 'category': 'Academic'},

            # Attendance
            {'code': 'attendance.view', 'name': 'View Attendance', 'app_label': 'attendance', 'resource': 'attendance', 'action': 'view', 'category': 'Academic'},
            {'code': 'attendance.create', 'name': 'Mark Attendance', 'app_label': 'attendance', 'resource': 'attendance', 'action': 'create', 'category': 'Academic'},

            # Reports
            {'code': 'reports.view_financial', 'name': 'View Financial Reports', 'app_label': 'reports', 'resource': 'financial', 'action': 'view', 'category': 'Financial'},
            {'code': 'reports.view_academic', 'name': 'View Academic Reports', 'app_label': 'reports', 'resource': 'academic', 'action': 'view', 'category': 'Academic'},
            {'code': 'reports.export', 'name': 'Export Reports', 'app_label': 'reports', 'resource': 'report', 'action': 'export', 'category': 'Administrative'},

            # System
            {'code': 'system.manage_roles', 'name': 'Manage Roles', 'app_label': 'core', 'resource': 'role', 'action': 'update', 'category': 'Administrative'},
            {'code': 'system.manage_users', 'name': 'Manage Users', 'app_label': 'accounts', 'resource': 'user', 'action': 'update', 'category': 'Administrative'},
            {'code': 'users.assign_role', 'name': 'Assign Roles to Users', 'app_label': 'accounts', 'resource': 'user', 'action': 'update', 'category': 'Administrative'},

            # Store/Inventory
            {'code': 'store.view', 'name': 'View Store Items', 'app_label': 'store', 'resource': 'item', 'action': 'view', 'category': 'Administrative'},
            {'code': 'store.create', 'name': 'Create Store Item', 'app_label': 'store', 'resource': 'item', 'action': 'create', 'category': 'Administrative'},
            {'code': 'store.approve', 'name': 'Approve Requisitions', 'app_label': 'store', 'resource': 'requisition', 'action': 'approve', 'category': 'Administrative'},

            # HR
            {'code': 'hr.view', 'name': 'View HR Records', 'app_label': 'hr', 'resource': 'employee', 'action': 'view', 'category': 'Administrative'},
            {'code': 'hr.create', 'name': 'Create Employee', 'app_label': 'hr', 'resource': 'employee', 'action': 'create', 'category': 'Administrative'},
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

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully seeded {created_count} permissions'))
