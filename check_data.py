#!/usr/bin/env python
"""
Diagnostic script to check database data for stats
Run: python check_data.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.base')
django.setup()

from apps.core.models import College
from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.accounts.models import User
from apps.academic.models import Class
from apps.fees.models import FeeCollection
from apps.attendance.models import StudentAttendance

print("=" * 80)
print("DATABASE DIAGNOSTIC CHECK")
print("=" * 80)

# Check colleges
print("\n1. COLLEGES:")
colleges = College.objects.all()
print(f"   Total colleges: {colleges.count()}")
for college in colleges:
    print(f"   - ID: {college.id}, Name: {college.name}, Code: {college.code}")

# Check students
print("\n2. STUDENTS:")
total_students = Student.objects.all().count()
print(f"   Total students (all): {total_students}")
if colleges.exists():
    for college in colleges:
        count = Student.objects.filter(college_id=college.id).count()
        print(f"   - College {college.id} ({college.code}): {count} students")

# Check teachers
print("\n3. TEACHERS:")
total_teachers = Teacher.objects.all().count()
print(f"   Total teachers (all): {total_teachers}")
if colleges.exists():
    for college in colleges:
        count = Teacher.objects.filter(college_id=college.id).count()
        print(f"   - College {college.id} ({college.code}): {count} teachers")

# Check users
print("\n4. USERS:")
total_users = User.objects.all().count()
print(f"   Total users (all): {total_users}")
if colleges.exists():
    for college in colleges:
        count = User.objects.filter(college_id=college.id).count()
        print(f"   - College {college.id} ({college.code}): {count} users")

# Check classes
print("\n5. CLASSES:")
total_classes = Class.objects.all().count()
print(f"   Total classes (all): {total_classes}")
if colleges.exists():
    for college in colleges:
        count = Class.objects.filter(college_id=college.id).count()
        print(f"   - College {college.id} ({college.code}): {count} classes")

# Check attendance
print("\n6. ATTENDANCE:")
total_attendance = StudentAttendance.objects.all().count()
print(f"   Total attendance records (all): {total_attendance}")
if colleges.exists():
    for college in colleges:
        count = StudentAttendance.objects.filter(student__college_id=college.id).count()
        print(f"   - College {college.id} ({college.code}): {count} records")

# Check fee collections
print("\n7. FEE COLLECTIONS:")
total_fees = FeeCollection.objects.all().count()
print(f"   Total fee collections (all): {total_fees}")
if colleges.exists():
    for college in colleges:
        count = FeeCollection.objects.filter(student__college_id=college.id).count()
        print(f"   - College {college.id} ({college.code}): {count} collections")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

if not colleges.exists():
    print("❌ NO COLLEGES FOUND! You need to create colleges first.")
elif total_students == 0:
    print("❌ NO STUDENTS FOUND! Database is empty.")
    print("   You need to add data to the database.")
else:
    print("✅ Data exists in database!")
    print(f"\n📋 TO USE STATS API:")
    print(f"   Use X-College-ID header with one of these college IDs:")
    for college in colleges:
        student_count = Student.objects.filter(college_id=college.id).count()
        print(f"   - College ID: {college.id} ({college.name}) - {student_count} students")

print("=" * 80)
