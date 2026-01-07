#!/usr/bin/env python
"""
Debug script to check current user and material issues visibility
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.accounts.models import User
from apps.store.models import MaterialIssueNote
from rest_framework.authtoken.models import Token

print("=" * 80)
print("DEBUG: Material Issues Visibility Check")
print("=" * 80)

# Get all tokens to find users
tokens = Token.objects.all()[:5]

print("\n📋 Recent Users with Tokens:")
print("-" * 80)
for token in tokens:
    user = token.user
    print(f"\nUsername: {user.username}")
    print(f"  User Type: {getattr(user, 'user_type', 'N/A')}")
    print(f"  College ID: {getattr(user, 'college_id', 'N/A')}")
    print(f"  Is Superuser: {user.is_superuser}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Token (first 20 chars): {token.key[:20]}...")

# Check material issues
print("\n" + "=" * 80)
print("📦 Material Issues in Database")
print("=" * 80)

total_issues = MaterialIssueNote.objects.count()
print(f"\nTotal Material Issues: {total_issues}")

if total_issues > 0:
    print("\n📊 Distribution by Receiving College:")
    print("-" * 80)
    
    from django.db.models import Count
    distribution = MaterialIssueNote.objects.values('receiving_college_id', 'receiving_college__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for item in distribution:
        college_name = item['receiving_college__name'] or 'Unknown'
        print(f"  College ID {item['receiving_college_id']} ({college_name}): {item['count']} issues")
    
    print("\n📋 Sample Material Issues:")
    print("-" * 80)
    for issue in MaterialIssueNote.objects.select_related('receiving_college')[:5]:
        print(f"\n  MIN: {issue.min_number}")
        print(f"    Status: {issue.status}")
        print(f"    Receiving College: {issue.receiving_college.name} (ID: {issue.receiving_college_id})")
        print(f"    Issue Date: {issue.issue_date}")
else:
    print("\n⚠️ No Material Issues found in database!")
    print("\nTo create sample data, run:")
    print("  python manage.py seed_material_issues")

# Check recent college admins
print("\n" + "=" * 80)
print("👥 College Admin Users")
print("=" * 80)

college_admins = User.objects.filter(user_type='college_admin')[:5]
if college_admins.exists():
    for user in college_admins:
        print(f"\nUsername: {user.username}")
        print(f"  College ID: {getattr(user, 'college_id', 'N/A')}")
        print(f"  Email: {user.email}")
        
        # Check how many issues they should see
        college_id = getattr(user, 'college_id', None)
        if college_id:
            visible_issues = MaterialIssueNote.objects.filter(receiving_college_id=college_id).count()
            print(f"  Should see {visible_issues} material issues")
        else:
            print(f"  ⚠️ No college_id - will see 0 issues")
else:
    print("\nNo college_admin users found")

print("\n" + "=" * 80)
