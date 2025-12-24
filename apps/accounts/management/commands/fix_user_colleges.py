"""
Management command to fix users with null colleges.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.core.models import College


class Command(BaseCommand):
    help = 'Fix users with null colleges by assigning the first available college'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Specific username to fix (if not provided, will list all users with null college)'
        )
        parser.add_argument(
            '--college-id',
            type=int,
            help='College ID to assign (if not provided, will use the first college)'
        )
        parser.add_argument(
            '--auto-fix',
            action='store_true',
            help='Automatically fix all users with null college'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        college_id = options.get('college_id')
        auto_fix = options.get('auto_fix')

        # Check available colleges
        colleges = College.objects.all_colleges()

        self.stdout.write("=" * 60)
        self.stdout.write("AVAILABLE COLLEGES:")
        self.stdout.write("=" * 60)

        if not colleges.exists():
            self.stdout.write(self.style.ERROR("No colleges found! Please create a college first."))
            return

        for college in colleges:
            self.stdout.write(f"ID: {college.id}, Code: {college.code}, Name: {college.name}")

        # Find college to assign
        if college_id:
            try:
                target_college = colleges.get(pk=college_id)
            except College.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"College with ID {college_id} not found!"))
                return
        else:
            target_college = colleges.first()
            self.stdout.write(f"\nUsing college: {target_college.name} (ID: {target_college.id})")

        # Find users with null college
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("USERS WITH NULL COLLEGE:")
        self.stdout.write("=" * 60)

        if username:
            users = User.objects.filter(username=username, college__isnull=True)
        else:
            users = User.objects.filter(college__isnull=True)

        if not users.exists():
            self.stdout.write(self.style.SUCCESS("No users with null college found!"))
            return

        for user in users:
            self.stdout.write(
                f"Username: {user.username}, Email: {user.email}, "
                f"Type: {user.user_type}, College: {user.college_id}"
            )

        # Fix users
        if auto_fix or username:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("FIXING USERS:")
            self.stdout.write("=" * 60)

            count = 0
            for user in users:
                old_college = user.college_id
                user.college = target_college

                # Also change user_type if it's super_admin
                if user.user_type == 'super_admin':
                    user.user_type = 'college_admin'
                    self.stdout.write(
                        self.style.WARNING(
                            f"Changing {user.username} from super_admin to college_admin"
                        )
                    )

                user.save()
                count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Updated {user.username}: college {old_college} -> {target_college.id}"
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(f"\nFixed {count} user(s)!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nTo fix these users, run with --auto-fix flag or specify --username"
                )
            )
