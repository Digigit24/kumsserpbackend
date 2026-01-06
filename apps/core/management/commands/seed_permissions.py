"""
Management command to seed default permissions for all colleges and roles.
"""
from django.core.management.base import BaseCommand
from apps.core.models import College, Permission
from apps.core.permissions.registry import get_default_permissions


class Command(BaseCommand):
    help = 'Seed default permissions for all colleges and roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--college',
            type=int,
            help='Seed permissions for a specific college ID (optional)'
        )
        parser.add_argument(
            '--role',
            type=str,
            help='Seed permissions for a specific role (optional)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing permissions'
        )

    def handle(self, *args, **options):
        college_id = options.get('college')
        role_filter = options.get('role')
        overwrite = options.get('overwrite', False)

        # Define roles to seed
        roles = ['admin', 'college_admin', 'central_manager', 'teacher', 'student', 'hod', 'staff', 'store_manager']

        if role_filter:
            if role_filter not in roles:
                self.stdout.write(self.style.ERROR(
                    f'Invalid role: {role_filter}. Valid roles: {", ".join(roles)}'
                ))
                return
            roles = [role_filter]

        # Get colleges to seed
        if college_id:
            colleges = College.objects.filter(id=college_id)
            if not colleges.exists():
                self.stdout.write(self.style.ERROR(f'College with ID {college_id} not found'))
                return
        else:
            colleges = College.objects.filter(is_active=True)

        if not colleges.exists():
            self.stdout.write(self.style.WARNING('No active colleges found'))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for college in colleges:
            for role in roles:
                permission, created = Permission.objects.all_colleges().get_or_create(
                    college=college,
                    role=role,
                    defaults={'permissions_json': get_default_permissions(role)}
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created permissions for {role} in {college.short_name}'
                    ))
                elif overwrite:
                    permission.permissions_json = get_default_permissions(role)
                    permission.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Updated permissions for {role} in {college.short_name}'
                    ))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'⊘ Skipped existing permissions for {role} in {college.short_name} '
                        f'(use --overwrite to update)'
                    ))

        self.stdout.write(self.style.SUCCESS(
            f'\n{" "*3}Summary:\n'
            f'  - Created: {created_count}\n'
            f'  - Updated: {updated_count}\n'
            f'  - Skipped: {skipped_count}\n'
            f'  - Total: {created_count + updated_count + skipped_count}'
        ))
