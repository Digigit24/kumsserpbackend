"""Seed common roles for all colleges."""
from django.core.management.base import BaseCommand
from apps.core.models import DynamicRole, College


class Command(BaseCommand):
    help = 'Seed common roles (Student, Teacher, Staff, etc.) for all colleges'

    def add_arguments(self, parser):
        parser.add_argument(
            '--college-id',
            type=int,
            help='Seed roles for specific college ID only'
        )

    def handle(self, *args, **options):
        college_id = options.get('college_id')

        # Define common roles that all colleges should have
        common_roles = [
            {
                'name': 'Student',
                'code': 'student',
                'description': 'Student enrolled in the college',
                'level': 10,
            },
            {
                'name': 'Teacher',
                'code': 'teacher',
                'description': 'Teaching staff member',
                'level': 5,
            },
            {
                'name': 'HOD',
                'code': 'hod',
                'description': 'Head of Department',
                'level': 4,
            },
            {
                'name': 'Principal',
                'code': 'principal',
                'description': 'College Principal/Head',
                'level': 2,
            },
            {
                'name': 'Staff',
                'code': 'staff',
                'description': 'Non-teaching staff member',
                'level': 7,
            },
            {
                'name': 'Store Manager',
                'code': 'store_manager',
                'description': 'Manages college store operations',
                'level': 6,
            },
            {
                'name': 'Librarian',
                'code': 'librarian',
                'description': 'Library management staff',
                'level': 7,
            },
            {
                'name': 'Accountant',
                'code': 'accountant',
                'description': 'Handles college accounts and finance',
                'level': 6,
            },
            {
                'name': 'Lab Assistant',
                'code': 'lab_assistant',
                'description': 'Laboratory technical assistant',
                'level': 8,
            },
        ]

        # Get colleges to seed
        if college_id:
            colleges = College.objects.filter(id=college_id, is_active=True)
            if not colleges.exists():
                self.stdout.write(self.style.ERROR(f'College with ID {college_id} not found'))
                return
        else:
            colleges = College.objects.filter(is_active=True)

        created_count = 0
        updated_count = 0

        for college in colleges:
            self.stdout.write(f'\nProcessing college: {college.name}')

            for role_data in common_roles:
                role, created = DynamicRole.objects.update_or_create(
                    college=college,
                    code=role_data['code'],
                    defaults={
                        'name': role_data['name'],
                        'description': role_data['description'],
                        'level': role_data['level'],
                        'is_active': True,
                        'is_global': False,
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Created role: {role.name}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ↻ Updated role: {role.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Completed! Created {created_count} roles, Updated {updated_count} roles'
            )
        )
