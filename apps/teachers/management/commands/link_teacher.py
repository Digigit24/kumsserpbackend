"""
Management command to link teacher profile to user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.teachers.models import Teacher
from apps.core.models import College

User = get_user_model()


class Command(BaseCommand):
    help = 'Link teacher profile to user goodluck'

    def handle(self, *args, **options):
        # Get the user
        try:
            user = User.objects.get(username='goodluck')
            self.stdout.write(f'✓ User: {user.username} (UUID: {user.id})')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ User "goodluck" not found!'))
            return

        # Check existing teachers
        all_teachers = Teacher.objects.all()
        self.stdout.write(f'\nTotal teachers: {all_teachers.count()}')

        for t in all_teachers:
            self.stdout.write(f'  Teacher ID {t.id}: user {t.user.username}')

        # Check if user has teacher profile
        existing = Teacher.objects.filter(user=user).first()

        if existing:
            self.stdout.write(self.style.SUCCESS(f'\n✓ User has teacher profile (ID: {existing.id})'))
            if not existing.is_active:
                existing.is_active = True
                existing.save()
                self.stdout.write(self.style.SUCCESS('  ✓ Activated!'))
        else:
            # Link first teacher to this user
            teacher = all_teachers.first()
            if teacher:
                self.stdout.write(f'\n→ Linking teacher ID {teacher.id} to user...')
                teacher.user = user
                teacher.is_active = True
                teacher.first_name = user.first_name or 'Good'
                teacher.last_name = user.last_name or 'Luck'
                teacher.email = user.email
                teacher.save()
                self.stdout.write(self.style.SUCCESS('✓ LINKED!'))
            else:
                # Create new teacher
                college = user.college or College.objects.first()
                teacher = Teacher.objects.create(
                    user=user,
                    college=college,
                    employee_id=f'EMP{str(user.id).replace("-", "")[:10]}',
                    joining_date='2025-01-01',
                    first_name=user.first_name or 'Good',
                    last_name=user.last_name or 'Luck',
                    date_of_birth='1990-01-01',
                    gender='Male',
                    email=user.email,
                    phone='1234567890',
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'\n✓ Created teacher (ID: {teacher.id})'))

        self.stdout.write(self.style.SUCCESS('\n✓ DONE! Restart server and try again.'))
