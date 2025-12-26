"""
Management command to create UserProfile for all users who don't have one.
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User, UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile for all users who don\'t have one'

    def handle(self, *args, **options):
        """Create user profiles for users without them."""
        self.stdout.write(self.style.NOTICE('Creating user profiles...'))

        # Get all users who have a college but no profile
        users_without_profile = User.objects.filter(college__isnull=False).exclude(
            id__in=UserProfile.objects.values_list('user_id', flat=True)
        )

        created_count = 0
        for user in users_without_profile:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'college': user.college}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created profile for user: {user.username} ({user.get_full_name()})'
                    )
                )

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total profiles created: {created_count}'))

        users_no_college = User.objects.filter(college__isnull=True).count()
        if users_no_college > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Users without profiles (no college assigned): {users_no_college}'
                )
            )

        # Show total stats
        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()
        self.stdout.write(self.style.NOTICE(f'Total users: {total_users}'))
        self.stdout.write(self.style.NOTICE(f'Total profiles: {total_profiles}'))
