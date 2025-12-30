#!/usr/bin/env python
"""
Fix teacher-user link for goodluck user
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.teachers.models import Teacher

User = get_user_model()

# Get the logged-in user
user = User.objects.get(username='goodluck')
print(f'User: {user.username} (UUID: {user.id})')

# Check existing teachers
all_teachers = Teacher.objects.all()
print(f'\nTotal teachers in database: {all_teachers.count()}')

for t in all_teachers:
    print(f'  Teacher ID {t.id}: linked to user {t.user.username} (UUID: {t.user.id})')

# Check if this user already has a teacher profile
existing = Teacher.objects.filter(user=user).first()

if existing:
    print(f'\n✓ User already has teacher profile (ID: {existing.id})')
    if not existing.is_active:
        existing.is_active = True
        existing.save()
        print('  ✓ Activated!')
else:
    # Link the first teacher to this user
    teacher = all_teachers.first()
    if teacher:
        print(f'\n→ Linking teacher ID {teacher.id} to user {user.username}...')
        teacher.user = user
        teacher.is_active = True
        teacher.save()
        print('✓ LINKED!')
    else:
        # Create new teacher
        from apps.core.models import College
        college = user.college or College.objects.first()

        teacher = Teacher.objects.create(
            user=user,
            college=college,
            employee_id=f'EMP{user.id.hex[:10]}',
            joining_date='2025-01-01',
            first_name=user.first_name or 'Teacher',
            last_name=user.last_name or 'User',
            date_of_birth='1990-01-01',
            gender='Male',
            email=user.email,
            phone='1234567890',
            is_active=True
        )
        print(f'\n✓ Created new teacher (ID: {teacher.id})')

print('\n✓ DONE! Now restart server and try again.')
