# Central Store API Flow & Endpoints

## Overview
Central store controlled by **Super Admin only**. College stores request materials through a two-level approval process.

## Approval Flow
```
College Store Manager → College Admin → Super Admin → Central Store → College
```

## Status Progression
1. `draft` - Initial creation
2. `pending_college_approval` - Submitted by college store manager
3. `pending_super_admin` - Approved by college admin
4. `super_admin_approved` - Approved by super admin (ready for central store)
5. `fulfilled` - Materials issued to college

## Rejection Statuses
- `rejected_by_college` - Rejected by college admin
- `rejected_by_super_admin` - Rejected by super admin

---

## API Endpoints

### 1. Central Store Inventory (Super Admin Only)

#### List Central Store Items
```
GET /api/v1/store/central-inventory/
Permissions: Any authenticated user (read)
Returns: All central store inventory items
```

#### Create Central Store Item
```
POST /api/v1/store/central-inventory/
Permissions: Super Admin only
Body: {
  "central_store": 1,
  "item": 5,
  "quantity_on_hand": 1000,
  "min_stock_level": 100,
  "reorder_point": 200
}
```

#### Update/Delete Central Store Item
```
PUT/PATCH/DELETE /api/v1/store/central-inventory/{id}/
Permissions: Super Admin only
```

---

### 2. Store Indents (Material Requests)

#### Create Indent
```
POST /api/v1/store/indents/
Permissions: College Store Manager
Body: {
  "college": 1,
  "central_store": 1,
  "required_by_date": "2026-01-15",
  "priority": "medium",
  "justification": "Required for lab",
  "items": [
    {
      "central_store_item": 5,
      "requested_quantity": 50,
      "unit": "pieces"
    }
  ]
}
```

#### Submit to College Admin
```
POST /api/v1/store/indents/{id}/submit/
Permissions: College Store Manager
Response: {"status": "pending_college_approval"}
```

#### College Admin - View Pending Approvals
```
GET /api/v1/store/indents/pending_college_approvals/
Permissions: College Admin or Super Admin
Returns: Indents with status "pending_college_approval" for their college
```

#### College Admin - Approve Indent
```
POST /api/v1/store/indents/{id}/college_admin_approve/
Permissions: College Admin
Response: {"status": "pending_super_admin"}
```

#### College Admin - Reject Indent
```
POST /api/v1/store/indents/{id}/college_admin_reject/
Permissions: College Admin
Body: {"reason": "Insufficient justification"}
Response: {"status": "rejected_by_college"}
```

#### Super Admin - View Pending Approvals
```
GET /api/v1/store/indents/pending_super_admin_approvals/
Permissions: Super Admin only
Returns: Indents with status "pending_super_admin"
```

#### Super Admin - Approve Indent
```
POST /api/v1/store/indents/{id}/super_admin_approve/
Permissions: Super Admin only
Response: {"status": "super_admin_approved"}
```

#### Super Admin - Reject Indent
```
POST /api/v1/store/indents/{id}/super_admin_reject/
Permissions: Super Admin only
Body: {"reason": "Budget constraints"}
Response: {"status": "rejected_by_super_admin"}
```

---

### 3. Material Issue (Central Store Fulfillment)

#### Issue Materials to College
```
POST /api/v1/store/indents/{id}/issue_materials/
Permissions: Super Admin only
Requires: Indent status must be "super_admin_approved"
Body: {
  "issue_date": "2026-01-10",
  "items": [
    {
      "central_store_item": 5,
      "quantity_issued": 50
    }
  ]
}
```

#### View Material Issues
```
GET /api/v1/store/material-issues/
Permissions: College Store Manager (their college), Super Admin (all)
```

#### Confirm Receipt
```
POST /api/v1/store/material-issues/{id}/confirm_receipt/
Permissions: College Store Manager
```

---

## Permissions Summary

### Super Admin
- Full access to central store inventory (CRUD)
- Approve/reject indents after college admin approval
- Issue materials to colleges
- View all indents and material issues

### College Admin
- Approve/reject indents from their college store
- View indents for their college
- View central store inventory (read-only)

### College Store Manager
- Create and submit indents
- View central store inventory (read-only)
- View their college's indents
- Confirm receipt of materials

---

## Complete Flow Example

1. **College Store Manager** creates indent
   ```
   POST /api/v1/store/indents/
   Status: draft
   ```

2. **College Store Manager** submits to college admin
   ```
   POST /api/v1/store/indents/1/submit/
   Status: pending_college_approval
   ```

3. **College Admin** views pending requests
   ```
   GET /api/v1/store/indents/pending_college_approvals/
   ```

4. **College Admin** approves
   ```
   POST /api/v1/store/indents/1/college_admin_approve/
   Status: pending_super_admin
   ```

5. **Super Admin** views pending requests
   ```
   GET /api/v1/store/indents/pending_super_admin_approvals/
   ```

6. **Super Admin** approves
   ```
   POST /api/v1/store/indents/1/super_admin_approve/
   Status: super_admin_approved
   ```

7. **Super Admin** issues materials
   ```
   POST /api/v1/store/indents/1/issue_materials/
   Status: partially_fulfilled/fulfilled
   ```

8. **College Store Manager** confirms receipt
   ```
   POST /api/v1/store/material-issues/1/confirm_receipt/
   ```

---

## Key Changes from Previous Implementation

1. **Central Store Access**: Now restricted to Super Admin only (was previously accessible to central store managers)

2. **Two-Level Approval**: Indents now require both college admin and super admin approval (was single approval)

3. **New Statuses**: Added granular statuses to track approval at each level

4. **Permission Updates**:
   - `IsCentralStoreManager` → Super Admin only
   - `CanApproveIndent` → College Admin or Super Admin
   - College-specific validation in approval endpoints

5. **Material Issuance**: Only possible after super admin approval
