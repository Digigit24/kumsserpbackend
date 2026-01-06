from apps.core.models import College
from apps.store.models import CentralStore, StoreIndent, MaterialIssueNote
from apps.accounts.models import User
from datetime import date, timedelta

try:
    print("Cleaning up old data...")
    try:
        if hasattr(MaterialIssueNote.objects, 'all_colleges'):
             MaterialIssueNote.objects.all_colleges().filter(min_number='MIN-2026-00010').delete()
        else:
             MaterialIssueNote.objects.filter(min_number='MIN-2026-00010').delete()
    except Exception as e:
        print(f"Error cleaning MIN: {e}")

    try:
        if hasattr(StoreIndent.objects, 'all_colleges'):
            StoreIndent.objects.all_colleges().filter(indent_number='IND-2026-00002').delete()
        else:
            StoreIndent.objects.filter(indent_number='IND-2026-00002').delete()
    except Exception as e:
         print(f"Error cleaning Indent: {e}")

    print("Creating new data...")
    college = College.objects.get(id=3)
    central_store = CentralStore.objects.first()
    # user = User.objects.filter(is_superuser=True).first()

    indent = StoreIndent.objects.create(
        indent_number='IND-2026-00002',
        college=college,
        central_store=central_store,
        indent_date=date.today(),
        required_by_date=date.today() + timedelta(days=7),
        priority='high',
        status='approved',
        justification='Required for semester operations'
    )

    MaterialIssueNote.objects.create(
        min_number='MIN-2026-00010',
        indent=indent,
        central_store=central_store,
        receiving_college=college,
        issue_date=date.today(),
        status='prepared'
    )

    print("Task Completed Successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
