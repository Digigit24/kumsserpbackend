#!/usr/bin/env python
"""
Quick test script to verify all URL modules can be imported without errors.
This simulates what Django does when starting the server.
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, '/home/user/kumsserpbackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings')

# Setup Django
django.setup()

print("Testing URL imports...")
print("-" * 60)

# List of all URL modules from kumss_erp/urls.py
url_modules = [
    'apps.core.urls',
    'apps.accounts.urls',
    'apps.academic.urls',
    'apps.students.urls',
    'apps.teachers.urls',
    'apps.attendance.urls',
    'apps.examinations.urls',
    'apps.fees.urls',
    'apps.library.urls',
    'apps.hostel.urls',
    'apps.hr.urls',
    'apps.accounting.urls',
    'apps.communication.urls',
    'apps.online_exam.urls',
    'apps.reports.urls',
    'apps.store.urls',
]

errors = []
for module_name in url_modules:
    try:
        __import__(module_name)
        print(f"✓ {module_name}")
    except Exception as e:
        errors.append((module_name, str(e)))
        print(f"✗ {module_name}: {e}")

print("-" * 60)
if errors:
    print(f"\n❌ Found {len(errors)} error(s):")
    for module, error in errors:
        print(f"  - {module}: {error}")
    sys.exit(1)
else:
    print("\n✅ All URL modules imported successfully!")
    print("Django server should start without URL import errors.")
    sys.exit(0)
