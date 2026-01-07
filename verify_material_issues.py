#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import MaterialIssueNote
from django.db.models import Count

print("=" * 70)
print("Material Issues After Seeding")
print("=" * 70)

total = MaterialIssueNote.objects.count()
print(f"\n✅ Total Material Issues: {total}")

if total > 0:
    print("\n📊 Distribution by College and Status:")
    print("-" * 70)
    
    dist = MaterialIssueNote.objects.values(
        'receiving_college_id', 
        'receiving_college__name',
        'status'
    ).annotate(count=Count('id')).order_by('receiving_college_id', 'status')
    
    for d in dist:
        college_name = d['receiving_college__name'] or 'Unknown'
        print(f"  College {d['receiving_college_id']} ({college_name})")
        print(f"    Status: {d['status']}, Count: {d['count']}")
    
    print("\n📋 Recent Material Issues:")
    print("-" * 70)
    for issue in MaterialIssueNote.objects.select_related('receiving_college')[:10]:
        print(f"  {issue.min_number} - {issue.status} - College: {issue.receiving_college.name}")

print("\n" + "=" * 70)
print("✅ Data seeded successfully!")
print("\nNow test the API:")
print("  GET http://127.0.0.1:8000/api/v1/store/material-issues/")
print("=" * 70)
