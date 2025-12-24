#!/usr/bin/env python
"""
Quick script to check colleges and users in the database.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.base')
django.setup()

from apps.core.models import College
from apps.accounts.models import User

print("=" * 60)
print("COLLEGES IN DATABASE:")
print("=" * 60)
colleges = College.objects.all_colleges()
if colleges.exists():
    for college in colleges:
        print(f"ID: {college.id}, Code: {college.code}, Name: {college.name}")
else:
    print("No colleges found in database!")

print("\n" + "=" * 60)
print("USERS IN DATABASE:")
print("=" * 60)
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}")
    print(f"  User Type: {user.user_type}")
    print(f"  College ID: {user.college_id} (College: {user.college})")
    print(f"  Is Active: {user.is_active}, Is Staff: {user.is_staff}")
    print()
