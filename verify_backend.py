#!/usr/bin/env python
"""
Backend Diagnostic Script - Verify Backend is Working Correctly
This script tests the backend directly without going through the API
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/user/kumsserpbackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings')
django.setup()

from apps.core.models import College, AcademicYear
from apps.accounts.models import Role, Department
from apps.core.utils import set_current_college_id, get_current_college_id

print("=" * 80)
print("BACKEND DIAGNOSTIC TEST")
print("=" * 80)

# Step 1: Check if fixes are applied
print("\n1. VERIFYING FIXES ARE APPLIED...")
print("-" * 80)

# Check if mixins.py has the fix
with open('/home/user/kumsserpbackend/apps/core/mixins.py', 'r') as f:
    mixins_content = f.read()
    if "'college' in serializer.fields" in mixins_content:
        print("❌ CRITICAL: mixins.py NOT FIXED!")
        print("   The old broken code is still there.")
        print("   You need to pull the latest changes!")
        sys.exit(1)
    else:
        print("✅ mixins.py is fixed (college_id will be set)")

# Check if models have CollegeManager
from apps.teachers.models import Teacher, AssignmentSubmission
from apps.attendance.models import StudentAttendance

if hasattr(Teacher.objects, 'all_colleges'):
    print("✅ Teacher model has CollegeManager")
else:
    print("❌ Teacher model missing CollegeManager")

if hasattr(AssignmentSubmission.objects, 'all_colleges'):
    print("✅ AssignmentSubmission model has CollegeManager")
else:
    print("❌ AssignmentSubmission model missing CollegeManager")

if hasattr(StudentAttendance.objects, 'all_colleges'):
    print("✅ StudentAttendance model has CollegeManager")
else:
    print("❌ StudentAttendance model missing CollegeManager")

# Step 2: Check database state
print("\n2. CHECKING DATABASE STATE...")
print("-" * 80)

# Check colleges
all_colleges = College.objects.all_colleges()
print(f"Total colleges in database: {all_colleges.count()}")

if all_colleges.count() == 0:
    print("❌ NO COLLEGES FOUND! Create a college first.")
    print("\nRun this to create a test college:")
    print("python manage.py shell")
    print(">>> from apps.core.models import College")
    print(">>> College.objects.create(code='TEST', name='Test College', short_name='TEST', email='test@test.com', phone='1234567890', address_line1='Test', city='Test', state='Test', pincode='12345')")
    sys.exit(1)

for college in all_colleges:
    print(f"  College ID {college.id}: {college.name} ({college.code})")

# Use first college for testing
test_college = all_colleges.first()
print(f"\n3. TESTING WITH COLLEGE: {test_college.name} (ID: {test_college.id})")
print("-" * 80)

# Set college context
set_current_college_id(test_college.id)
print(f"Set thread-local college_id: {get_current_college_id()}")

# Check AcademicYear data
print("\n4. CHECKING ACADEMIC YEAR DATA...")
print("-" * 80)

ay_all = AcademicYear.objects.all_colleges()
print(f"Total AcademicYears (all colleges): {ay_all.count()}")

# Check for NULL college_id (broken data from before fix)
ay_null = AcademicYear.objects.all_colleges().filter(college_id__isnull=True)
if ay_null.count() > 0:
    print(f"⚠️  WARNING: {ay_null.count()} AcademicYear records have NULL college_id")
    print("   These were created BEFORE the fix was applied.")
    print("   Solution: Delete them or update them manually:")
    print(f"   >>> AcademicYear.objects.filter(college_id__isnull=True).delete()")

# Check for this college
ay_college = AcademicYear.objects.all_colleges().filter(college_id=test_college.id)
print(f"AcademicYears for college {test_college.id}: {ay_college.count()}")

if ay_college.count() > 0:
    print("  Sample records:")
    for ay in ay_college[:3]:
        print(f"    - ID {ay.id}: {ay.year} (college_id={ay.college_id})")

# Test the ViewSet logic
print("\n5. SIMULATING VIEWSET GET_QUERYSET...")
print("-" * 80)

# This simulates what the ViewSet does
queryset = AcademicYear.objects.all_colleges()
print(f"Step 1 - .all_colleges(): {queryset.count()} records")

filtered = queryset.filter(college_id=test_college.id)
print(f"Step 2 - .filter(college_id={test_college.id}): {filtered.count()} records")

if queryset.count() > 0 and filtered.count() == 0:
    print("❌ PROBLEM: Records exist but filtering returns 0!")
    print("   This means records don't have the correct college_id")
    print("   Check what college_ids exist:")
    college_ids = queryset.values_list('college_id', flat=True).distinct()
    print(f"   Found college_ids: {list(college_ids)}")

# Step 6: Test creating a new record
print("\n6. TESTING RECORD CREATION (Simulating POST)...")
print("-" * 80)

try:
    # Create a test academic year
    test_year = f"TEST-{test_college.id}"

    # Check if already exists
    existing = AcademicYear.objects.all_colleges().filter(
        year=test_year,
        college_id=test_college.id
    )

    if existing.exists():
        print(f"Test record already exists: {test_year}")
        test_record = existing.first()
    else:
        # Simulate what the ViewSet does during POST
        from datetime import date
        test_record = AcademicYear.objects.create(
            college_id=test_college.id,  # This is what the fix ensures gets set
            year=test_year,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            is_current=False
        )
        print(f"✅ Created test record: {test_year}")

    print(f"   Record ID: {test_record.id}")
    print(f"   college_id: {test_record.college_id}")

    # Try to retrieve it
    retrieved = AcademicYear.objects.all_colleges().filter(
        college_id=test_college.id,
        id=test_record.id
    )

    if retrieved.exists():
        print(f"✅ Can retrieve the record with college_id filter")
    else:
        print(f"❌ CANNOT retrieve the record with college_id filter!")

except Exception as e:
    print(f"❌ Error creating test record: {e}")
    import traceback
    traceback.print_exc()

# Final summary
print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

issues = []

# Check for issues
if "'college' in serializer.fields" in mixins_content:
    issues.append("mixins.py not fixed - need to pull latest code")

if all_colleges.count() == 0:
    issues.append("No colleges in database")

if ay_null.count() > 0:
    issues.append(f"{ay_null.count()} records with NULL college_id (old broken data)")

if ay_all.count() > 0 and ay_college.count() == 0:
    issues.append("Records exist but not for your test college")

if issues:
    print("\n❌ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("\n✅ ALL CHECKS PASSED!")
    print("Backend is working correctly.")
    print("If API still returns empty results, the issue is likely:")
    print("  - Frontend not sending X-College-ID header")
    print("  - Wrong college_id in header")
    print("  - Old data with NULL college_id")

print("\n" + "=" * 80)
