#!/usr/bin/env python
"""
Check MaterialIssueNote data in database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from apps.store.models import MaterialIssueNote

print("=" * 70)
print("Checking MaterialIssueNote Table Data")
print("=" * 70)

# Check if table exists and has data
try:
    total_count = MaterialIssueNote.objects.count()
    print(f"\n✅ Total records in material_issue_note table: {total_count}")
    
    if total_count > 0:
        print("\n📋 Sample Records (first 5):")
        print("-" * 70)
        
        for issue in MaterialIssueNote.objects.all()[:5]:
            print(f"\nID: {issue.id}")
            print(f"  MIN Number: {issue.min_number}")
            print(f"  Status: {issue.status}")
            print(f"  Issue Date: {issue.issue_date}")
            print(f"  Receiving College ID: {issue.receiving_college_id}")
            print(f"  Central Store ID: {issue.central_store_id}")
            print(f"  Indent ID: {issue.indent_id}")
        
        print("\n" + "=" * 70)
        print("📊 Status Distribution:")
        print("-" * 70)
        from django.db.models import Count
        status_counts = MaterialIssueNote.objects.values('status').annotate(count=Count('status'))
        for item in status_counts:
            print(f"  {item['status']}: {item['count']} records")
        
        print("\n" + "=" * 70)
        print("🏢 College Distribution:")
        print("-" * 70)
        college_counts = MaterialIssueNote.objects.values('receiving_college_id').annotate(count=Count('id'))
        for item in college_counts:
            print(f"  College ID {item['receiving_college_id']}: {item['count']} records")
            
    else:
        print("\n⚠️ Table is empty! No records found.")
        print("\nTo add test data, run:")
        print("  python manage.py seed_material_issues")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Checking View Configuration")
print("=" * 70)

from apps.store.views import MaterialIssueNoteViewSet
print(f"\nBase Class: {MaterialIssueNoteViewSet.__bases__}")
print(f"Related College Lookup: {getattr(MaterialIssueNoteViewSet, 'related_college_lookup', 'Not set')}")

print("\n⚠️ IMPORTANT: This view uses RelatedCollegeScopedModelViewSet")
print("   This means it filters by receiving_college_id based on the user's college.")
print("   If the logged-in user's college doesn't match the data, results will be empty.")
