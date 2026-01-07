# Material Issues Visibility for Different User Types

## Overview

Material Issues (Material Issue Notes / MIN) represent materials being dispatched from Central Store to Colleges. They are created after indents are approved.

## User Access Matrix

### 🔐 Who Can See What?

| User Type                                                 | What They See                                                                      | Why                                                       |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Super Admin**                                           | All material issues                                                                | Global oversight                                          |
| **Staff**                                                 | All material issues                                                                | Administrative access                                     |
| **Central Store Manager** (`user_type='central_manager'`) | All material issues                                                                | They create and dispatch all MINs                         |
| **College Admin** (`user_type='college_admin'`)           | Only issues for **their college** (where `receiving_college_id = user.college_id`) | They need to track incoming materials and confirm receipt |
| **College Store Manager**                                 | Only issues for **their college**                                                  | They receive the materials                                |
| **Others**                                                | No access                                                                          | N/A                                                       |

## Current Implementation

**File:** `apps/store/views.py` - `MaterialIssueNoteViewSet`

```python
def get_queryset(self):
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
        return queryset.filter(receiving_college_id=college_id)  # ✅ Their college only

    return queryset.none()  # ❌ No college = no access
```

## Workflow: How Material Issues Work

1. **College Store Manager** creates an indent
2. **College Admin** approves the indent
3. **Super Admin** approves the indent
4. **Central Store Manager** creates Material Issue Note (MIN) from approved indent
5. **Central Store Manager** marks MIN as "dispatched"
6. **College Store Manager/Admin** confirms receipt when materials arrive

## Why College Admins SHOULD See Material Issues

✅ **College admins need this feature** because:

1. **Track Incoming Materials** - Know what's being sent from central store
2. **Monitor Dispatch Status** - See if materials are prepared, dispatched, in transit, or received
3. **Confirm Receipt** - Mark materials as received when they arrive
4. **Audit Trail** - Track all materials received by their college

## If College Admin Sees Empty Results

### Possible Reasons:

1. **No data for their college** - No material issues have been created for their `college_id`
2. **User has no `college_id`** - Check: `user.college_id` should not be None
3. **No approved indents yet** - Material issues are created only after indents are super_admin_approved

### Solutions:

#### Option 1: Seed Test Data

```bash
python manage.py seed_material_issues
```

#### Option 2: Create Material Issue from Approved Indent

1. Go to Indents API: `/api/v1/store/indents/`
2. Find an indent with `status='super_admin_approved'`
3. Call: `POST /api/v1/store/indents/{id}/issue_materials/`
   ```json
   {
     "issue_date": "2026-01-06",
     "issued_by": "<user_id>",
     "items": [...]
   }
   ```

#### Option 3: Verify User's College ID

```python
from apps.accounts.models import User
user = User.objects.get(username='your_college_admin')
print(f"College ID: {user.college_id}")  # Should NOT be None

# If None, update it:
from apps.core.models import College
college = College.objects.first()
user.college = college
user.save()
```

## Frontend Implementation

### ✅ KEEP Material Issues in College Admin Frontend

**Show in sidebar/menu:**

- Menu item: "Material Issues" or "Incoming Materials"
- Route: `/store/material-issues` or `/store/incoming-materials`

**Features to show:**

1. **List View:**

   - MIN Number
   - Status (Prepared, Dispatched, In Transit, Received)
   - Issue Date
   - Items included
   - Dispatch/Receipt dates

2. **Status Filtering:**

   - Filter by status to see pending, in-transit, or received materials

3. **Actions:**
   - View details
   - Confirm receipt (when status is 'dispatched' or 'in_transit')
   - Download MIN PDF

### ❌ DON'T Remove This Feature

College admins need visibility into materials coming to their college. This is a critical part of the inventory management workflow.

## Testing

### Check if College Admin Can See Material Issues

1. **Login as college admin**
2. **Call API:**

   ```
   GET /api/v1/store/material-issues/
   Authorization: Token <college_admin_token>
   ```

3. **Expected Result:**
   ```json
   {
     "count": N,
     "results": [
       {
         "id": 1,
         "min_number": "MIN-2026-00001",
         "status": "dispatched",
         "receiving_college_id": <matches user.college_id>
         ...
       }
     ]
   }
   ```

### If Empty:

- Check `user.college_id` exists
- Check if any material issues exist for that college in database
- Seed test data if needed

---

**Conclusion:** ✅ **KEEP Material Issues visible to College Admins** - they need it to track incoming materials!
