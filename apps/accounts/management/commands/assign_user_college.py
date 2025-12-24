"""
Management command to assign a college to a user.
"""
from django.core.management.base import BaseCommand, CommandError
from apps.accounts.models import User
from apps.core.models import College


class Command(BaseCommand):
    help = 'Assign a college to a user by username or email'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_identifier',
            type=str,
            help='Username or email of the user'
        )
        parser.add_argument(
            'college_id',
            type=int,
            help='College ID to assign to the user'
        )
        parser.add_argument(
            '--change-type',
            type=str,
            choices=['college_admin', 'teacher', 'student', 'staff'],
            help='Also change user type (recommended when assigning college to super_admin)'
        )

    def handle(self, *args, **options):
        user_identifier = options['user_identifier']
        college_id = options['college_id']
        change_type = options.get('change_type')

        # Find user
        try:
            user = User.objects.filter(
                username=user_identifier
            ).first() or User.objects.filter(
                email=user_identifier
            ).first()

            if not user:
                raise CommandError(f'User "{user_identifier}" not found')
        except Exception as e:
            raise CommandError(f'Error finding user: {str(e)}')

        # Find college
        try:
            college = College.objects.all_colleges().get(pk=college_id)
        except College.DoesNotExist:
            raise CommandError(f'College with ID {college_id} not found')

        # Update user
        old_college = user.college
        old_type = user.user_type

        user.college = college

        if change_type:
            user.user_type = change_type

        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully updated user "{user.username}":\n'
                f'  College: {old_college} -> {college.name}\n'
                f'  User Type: {old_type} -> {user.user_type}\n'
            )
        )
