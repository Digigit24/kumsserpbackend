#!/usr/bin/env python
"""
Script to create teacher profile for user 'goodluck'
Run this with: python create_teacher_profile.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.teachers.models import Teacher
from apps.core.models import College

User = get_user_model()

def create_teacher_profile():
    # Get user
    try:
        user = User.objects.get(username='goodluck')
        print(f'✓ Found user: {user.username} (UUID: {user.id})')
    except User.DoesNotExist:
        print('✗ User "goodluck" not found!')
        return

    # Check if teacher profile already exists
    teacher = Teacher.objects.filter(user=user).first()
    if teacher:
        print(f'✓ Teacher profile already exists!')
        print(f'  Teacher ID: {teacher.id}')
        print(f'  Employee ID: {teacher.employee_id}')
        print(f'  Active: {teacher.is_active}')

        if not teacher.is_active:
            teacher.is_active = True
            teacher.save()
            print(f'  ✓ Activated teacher profile')

        return

    # Get college
    college = user.college
    if not college:
        college = College.objects.first()
        if not college:
            print('✗ No college found! Create a college first.')
            return

    # Create teacher profile
    teacher = Teacher.objects.create(
        user=user,
        college=college,
        employee_id=f'TEACH{user.id}'.replace('-', '')[:20],
        joining_date='2025-01-01',
        first_name=user.first_name or 'Good',
        last_name=user.last_name or 'Luck',
        date_of_birth='1990-01-01',
        gender='Male',
        email=user.email or 'teacher@example.com',
        phone='1234567890',
        is_active=True
    )

    print(f'✓ SUCCESS! Teacher profile created!')
    print(f'  Teacher ID: {teacher.id}')
    print(f'  Employee ID: {teacher.employee_id}')
    print(f'  Name: {teacher.get_full_name()}')
    print(f'\n✓ Now you can create assignments!')
    print(f'  Remove "teacher" field from request - backend will auto-populate it.')

if __name__ == '__main__':
    create_teacher_profile()
