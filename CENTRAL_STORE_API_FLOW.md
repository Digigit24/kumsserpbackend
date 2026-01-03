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



we tried our best but the error still exist now we will create

a new centraal store through the super admin only give all permissions regarding the central store to the super admin

all the college's specific store which will be only accessible to that clg store and that specific clg admin and super admin

now the flow will be like :
the central store will have all the inventries the specific clg store will send the request to the central store for oreders and the same request will go to the specific clg admin and if the clg admin accepts the request it goes to the super admin and if super admin grants the aproval it send it to central store to grant the order and then the specific clg gets the oreder from the central store

the specific clg will have the access to see the inventery of the central store while placing the order

this will be the flow ok

the central store will also be the independent store like other stores but only controled by super admin

now change the apis if needed in the backend and return me the exact flow with all the changes in the backend from approvals to permissions to apis iof needed bcz tomaarrow is the dead line to submit the project so i need it very urgently also make a md file which will contain the endpoints from whic api what will perform use less tokens for this


AzXYW
Done! Complete two-level approval system implemented. Here's what changed:

Changes Made
1. Permissions (apps/store/permissions.py)
Central store now super-admin only
College admins can approve indents for their college
Super admin has full access
2. Models (apps/store/models.py)
New statuses: pending_college_approval, pending_super_admin, super_admin_approved, rejected_by_college, rejected_by_super_admin
New methods:
college_admin_approve() - College admin approves → super admin
college_admin_reject() - College admin rejects
super_admin_approve() - Super admin approves → central store
super_admin_reject() - Super admin rejects
3. Views (apps/store/views.py)
New endpoints:
POST /api/v1/store/indents/{id}/college_admin_approve/
POST /api/v1/store/indents/{id}/college_admin_reject/
POST /api/v1/store/indents/{id}/super_admin_approve/
POST /api/v1/store/indents/{id}/super_admin_reject/
GET /api/v1/store/indents/pending_college_approvals/
GET /api/v1/store/indents/pending_super_admin_approvals/
4. Serializers (apps/store/serializers.py)
Fixed central store item validation - any college can now access central items
5. Documentation (CENTRAL_STORE_API_FLOW.md)
Complete API reference with all endpoints
Flow diagrams
Permission matrix
Example requests
Approval Flow
College Store → Submit → College Admin → Approve → Super Admin → Approve → Central Store → Issue Materials → College

