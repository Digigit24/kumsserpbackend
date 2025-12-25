#!/usr/bin/env python
"""
Test script to verify college data is being saved and retrieved correctly.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/user/kumsserpbackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings')
django.setup()

from apps.core.models import College, AcademicYear, AcademicSession, Holiday, Weekend
from apps.accounts.models import Role, UserRole, Department
from apps.core.utils import set_current_college_id, get_current_college_id

print("=" * 80)
print("COLLEGE DATA DIAGNOSTIC TEST")
print("=" * 80)

# Check if any colleges exist
print("\n1. Checking College records...")
colleges = College.objects.all_colleges()
print(f"   Total colleges in database: {colleges.count()}")
for college in colleges[:5]:
    print(f"   - {college.id}: {college.name} ({college.code})")

if colleges.count() == 0:
    print("   ⚠️  WARNING: No colleges found in database!")
    print("   You need to create a College record first.")
    sys.exit(1)

# Test with first college
test_college = colleges.first()
print(f"\n2. Testing with college: {test_college.name} (ID: {test_college.id})")

# Set college context
set_current_college_id(test_college.id)
print(f"   Set thread-local college_id: {get_current_college_id()}")

# Check each model
models_to_check = [
    ('AcademicYear', AcademicYear),
    ('AcademicSession', AcademicSession),
    ('Holiday', Holiday),
    ('Weekend', Weekend),
    ('Role', Role),
    ('Department', Department),
]

print("\n3. Checking records per model...")
print("-" * 80)

for model_name, Model in models_to_check:
    # Get all records
    all_records = Model.objects.all_colleges()
    all_count = all_records.count()

    # Get records for current college
    college_records = Model.objects.filter(college_id=test_college.id)
    college_count = college_records.count()

    # Get records using for_current_college
    scoped_records = Model.objects.for_current_college()
    scoped_count = scoped_records.count()

    print(f"{model_name:20} | Total: {all_count:3} | College {test_college.id}: {college_count:3} | Scoped: {scoped_count:3}")

    if all_count > 0 and college_count == 0:
        print(f"   ⚠️  WARNING: {model_name} has records but NONE for college {test_college.id}")
        # Show which colleges these records belong to
        college_ids = all_records.values_list('college_id', flat=True).distinct()
        print(f"   Records exist for college IDs: {list(college_ids)}")

    if college_count > 0 and scoped_count == 0:
        print(f"   ⚠️  ERROR: Direct filter finds records but for_current_college doesn't!")

print("-" * 80)

# Test the queryset chain
print("\n4. Testing queryset chaining...")
print(f"   Thread-local college_id: {get_current_college_id()}")
qs1 = AcademicYear.objects.all_colleges()
print(f"   .all_colleges() count: {qs1.count()}")
qs2 = qs1.filter(college_id=test_college.id)
print(f"   .filter(college_id={test_college.id}) count: {qs2.count()}")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
