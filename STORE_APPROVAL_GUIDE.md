# Store Approval System - Implementation Guide

## Overview
The store app is fully integrated with the approval system. All procurement requirements, store indents, and goods inspections automatically create approval requests for college admins.

## Key Features Implemented

### 1. **Store Manager Role**
- **Role Code**: `store_manager`
- **Permissions**:
  - View, create, and edit store records
  - Create and submit store indents
  - Confirm receipt of materials
  - View inventory and reports
  - Create approval requests

**Migration**: `apps/store/migrations/0005_create_store_manager_role.py`

### 2. **Approval Integration**

#### Automatic Approval Request Creation
When these actions occur, approval requests are automatically created:

**Store Indent Submitted:**
- Trigger: `StoreIndent.status = 'submitted'`
- Request Type: `'store_indent'`
- Approvers: College admins/staff
- Details included: indent number, date, priority, items count, central store

**Procurement Requirement Submitted:**
- Trigger: `ProcurementRequirement.status = 'submitted'`
- Request Type: `'procurement_requirement'`
- Approvers: College admins/staff
- Details included: requirement number, dates, urgency, items count, estimated total

### 3. **Enhanced API Endpoints**

#### For College Admins - Approval Panel

**GET `/api/v1/approvals/approval-requests/store_requests/`**
- Returns all store-related approval requests (indents, procurement, inspections)
- Filtered by college
- Includes full details of related objects

**GET `/api/v1/approvals/approval-requests/pending_store_requests/`**
- Returns only pending store-related approval requests
- Used for the admin approval panel frontend

**GET `/api/v1/approvals/approval-requests/pending_approvals/`**
- Returns all pending approvals for current user (all types)

#### Approval Actions

**POST `/api/v1/approvals/approval-requests/{id}/review/`**
```json
{
  "action": "approve",  // or "reject"
  "comment": "Approved for procurement"
}
```

### 4. **Response Format**

Approval requests now include `related_object_details` field:

```json
{
  "id": 1,
  "request_type": "store_indent",
  "title": "Store Indent IND-2026-001",
  "status": "pending",
  "priority": "high",
  "related_object_details": {
    "indent_number": "IND-2026-001",
    "indent_date": "2026-01-03",
    "status": "pending_approval",
    "priority": "high",
    "justification": "Urgent requirement for lab equipment",
    "items_count": 5,
    "central_store": "Main Central Store"
  },
  "requester_details": {
    "id": "uuid",
    "username": "store.manager",
    "full_name": "John Doe"
  },
  "approvers_details": [...],
  ...
}
```

## Complete Workflow Examples

### Flow 1: College Store Manager Creates Indent

1. **Store Manager** creates indent via:
   ```
   POST /api/v1/store/indents/
   ```

2. **Store Manager** submits indent:
   ```
   POST /api/v1/store/indents/{id}/submit/
   ```

3. **System** automatically:
   - Changes indent status to `'pending_approval'`
   - Creates `ApprovalRequest` with type `'store_indent'`
   - Assigns college admin as approver
   - Sends notification to admin

4. **College Admin** sees request in approval panel:
   ```
   GET /api/v1/approvals/approval-requests/pending_store_requests/
   ```

5. **College Admin** approves:
   ```
   POST /api/v1/approvals/approval-requests/{id}/review/
   {
     "action": "approve",
     "comment": "Approved for central store"
   }
   ```

6. **System** automatically:
   - Updates approval request status to `'approved'`
   - Updates indent status to `'approved'`
   - Sends notification to store manager

7. **Central Manager** creates Material Issue Note:
   ```
   POST /api/v1/store/indents/{id}/issue_materials/
   ```

### Flow 2: Central Store Procurement

1. **Central Manager** creates requirement:
   ```
   POST /api/v1/store/procurement/requirements/
   ```

2. **Central Manager** submits for approval:
   ```
   POST /api/v1/store/procurement/requirements/{id}/submit_for_approval/
   ```

3. **System** creates approval request for CEO/Finance (college admin)

4. **College Admin** approves via approval panel

5. **System** updates requirement status to `'approved'`

6. **Suppliers** submit quotations

7. **CEO** selects best quotation

8. **Central Manager** creates Purchase Order

9. **Supplier** delivers goods

10. **Central Store** receives and posts to inventory

## Frontend Integration

### Approval Panel for College Admin

The frontend should fetch pending store approvals from:
```
GET /api/v1/approvals/approval-requests/pending_store_requests/?page=1&page_size=10
```

Display:
- Request type (Indent / Procurement / Inspection)
- Requester details
- Priority badge
- Submitted date
- Related object details (indent number, items count, etc.)
- Action buttons (Approve / Reject)

### Store Manager Dashboard

Show "My Requests" from:
```
GET /api/v1/approvals/approval-requests/my_requests/?request_type=store_indent
```

## Database Schema

### ApprovalRequest Fields
- `college`: ForeignKey to College
- `requester`: User who created the request
- `request_type`: 'store_indent' | 'procurement_requirement' | 'goods_inspection'
- `title`: Auto-generated title
- `description`: Justification from indent/requirement
- `priority`: Mapped from indent/requirement priority
- `status`: 'pending' | 'approved' | 'rejected' | 'cancelled'
- `approvers`: ManyToMany to User (college admins)
- `content_type` & `object_id`: Generic FK to StoreIndent/ProcurementRequirement
- `metadata`: JSON field for additional data

## Testing

1. Create a store manager user:
```python
from apps.accounts.models import User, Role, UserRole
user = User.objects.create_user(username='store.manager', user_type='staff')
role = Role.objects.get(code='store_manager', college_id=1)
UserRole.objects.create(user=user, role=role, college_id=1)
```

2. Create and submit an indent as store manager

3. Check approval panel as college admin

4. Approve the request

5. Verify indent status changed to 'approved'

## Summary

✅ Store Manager role created with appropriate permissions
✅ Approval requests auto-created when indents/requirements submitted
✅ College admins assigned as approvers automatically
✅ Enhanced serializers include store-specific details
✅ New endpoints for store approval panel
✅ Notifications sent to approvers and requesters
✅ Complete audit trail via ApprovalAction model

All store operations now flow through the approval system, providing full visibility and control for college administration.
