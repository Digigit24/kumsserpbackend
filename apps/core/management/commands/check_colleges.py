"""
Management command to check colleges and users in the database.
"""
from django.core.management.base import BaseCommand
from apps.core.models import College
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Check colleges and users in the database'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("COLLEGES IN DATABASE:")
        self.stdout.write("=" * 60)

        colleges = College.objects.all_colleges()
        if colleges.exists():
            for college in colleges:
                self.stdout.write(
                    f"ID: {college.id}, Code: {college.code}, Name: {college.name}"
                )
        else:
            self.stdout.write(self.style.WARNING("No colleges found in database!"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("USERS IN DATABASE:")
        self.stdout.write("=" * 60)

        users = User.objects.all()
        for user in users:
            self.stdout.write(f"\nUsername: {user.username}, Email: {user.email}")
            self.stdout.write(f"  User Type: {user.user_type}")
            self.stdout.write(f"  College ID: {user.college_id} (College: {user.college})")
            self.stdout.write(f"  Is Active: {user.is_active}, Is Staff: {user.is_staff}")
