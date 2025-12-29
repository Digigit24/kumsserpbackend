"""
Management command to create a superadmin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superadmin user with access to all colleges and all permissions'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username for the superadmin')
        parser.add_argument('--email', type=str, required=True, help='Email for the superadmin')
        parser.add_argument('--password', type=str, required=True, help='Password for the superadmin')
        parser.add_argument('--first-name', type=str, default='Super', help='First name')
        parser.add_argument('--last-name', type=str, default='Admin', help='Last name')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options.get('first_name', 'Super')
        last_name = options.get('last_name', 'Admin')

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User {username} already exists'))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_superadmin=True,
            is_staff=True,
            is_superuser=True,
            is_active=True,
            user_type='super_admin'
        )

        self.stdout.write(self.style.SUCCESS(
            f'Superadmin "{username}" created successfully!\n'
            f'  - Email: {email}\n'
            f'  - Has access to all colleges and all permissions'
        ))
