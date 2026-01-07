# Material Issue API - Empty Results Fix

## Problem

The API endpoint `/api/v1/store/material-issues/` was returning:

```json
{ "count": 0, "next": null, "previous": null, "results": [] }
```

## Root Cause

The `MaterialIssueNoteViewSet` was using `RelatedCollegeScopedModelViewSet` which filters records by `receiving_college_id`. This requires:

1. **Either** the request includes `X-College-ID` header matching the data's `receiving_college_id`
2. **Or** the user is a superuser/staff/central_manager

Without these, the queryset would return empty results even if data exists in the database.

## Solution Applied

### Changed the ViewSet Base Class

**File:** `apps/store/views.py`

**Before:**

```python
class MaterialIssueNoteViewSet(RelatedCollegeScopedModelViewSet):
    queryset = MaterialIssueNote.objects.select_related('indent', 'central_store', 'receiving_college')
    related_college_lookup = 'receiving_college_id'
    # ...
```

**After:**

```python
class MaterialIssueNoteViewSet(viewsets.ModelViewSet):
    queryset = MaterialIssueNote.objects.select_related('indent', 'central_store', 'receiving_college')
    permission_classes = [IsAuthenticated]
    # Added custom get_queryset method
```

### Added Custom Queryset Filtering

```python
def get_queryset(self):
    """
    Custom queryset filtering:
    - Superusers, staff, and central_managers see all material issues
    - College users see only material issues for their college
    """
    queryset = super().get_queryset()
    user = self.request.user

    # Global users see everything
    is_global_user = (
        user.is_superuser or
        user.is_staff or
        getattr(user, 'user_type', None) == 'central_manager'
    )

    if is_global_user:
        return queryset  # ✅ All records

    # College users see only their college's material issues
    college_id = getattr(user, 'college_id', None)
    if college_id:
        return queryset.filter(receiving_college_id=college_id)

    # No college? No results
    return queryset.none()
```

## How It Works Now

### For Superusers/Staff/Central Managers:

- ✅ See **all** material issues regardless of `receiving_college_id`
- ❌ No `X-College-ID` header needed

### For College Users:

- ✅ See material issues where `receiving_college_id` matches their `college_id`
- ✅ Automatic filtering based on `user.college_id`

### For Users Without College:

- ❌ Empty results (security measure)

## Testing

### 1. Check if you're a global user

```python
# In Django shell or check in database
user = User.objects.get(username='your_username')
print(f"Is Superuser: {user.is_superuser}")
print(f"Is Staff: {user.is_staff}")
print(f"User Type: {user.user_type}")
print(f"College ID: {user.college_id}")
```

### 2. Test the API

```bash
# With authentication token
GET http://127.0.0.1:8000/api/v1/store/material-issues/
Authorization: Token <your-token>
```

## If Still Empty

If you're still getting empty results, it means:

1. **No data exists** in `material_issue_note` table

   - Solution: Run `python manage.py seed_material_issues`

2. **User is not a global user** AND **their `college_id` doesn't match any `receiving_college_id`**

   - Solution: Either make user a superuser/central_manager, or seed data for their college

3. **Authentication issue** - User is not logged in
   - Solution: Check your auth token

## Quick Check Script

Run this to see your user details:

```python
from rest_framework.authtoken.models import Token
token = Token.objects.get(key='<your-token>')
user = token.user
print(f"Username: {user.username}")
print(f"Is Superuser: {user.is_superuser}")
print(f"User Type: {getattr(user, 'user_type', None)}")
print(f"College ID: {getattr(user, 'college_id', None)}")
```

---

**Status:** ✅ Fixed
**Date:** 2026-01-06 15:15 IST
