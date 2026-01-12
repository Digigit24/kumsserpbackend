# Store Module: Status Changes & deletion API Documentation

This document covers the specific API endpoints for changing statuses and deleting records within the Store, Procurement, and Transfers modules.

---

## 1. Store Indent Operations

### Change Status: Submit for Approval

**Endpoint:** `POST /api/store/indents/{id}/submit/`
**Action:** College Store Manager submits the indent to College Admin.
**Response:** `200 OK`

```json
{
  "status": "pending_college_approval"
}
```

### Change Status: College Admin Approve

**Endpoint:** `POST /api/store/indents/{id}/college_admin_approve/`
**Action:** College Admin approves and forwards to Super Admin.
**Response:** `200 OK`

```json
{
  "status": "pending_super_admin"
}
```

### Change Status: College Admin Reject

**Endpoint:** `POST /api/store/indents/{id}/college_admin_reject/`
**Request Payload:**

```json
{
  "rejection_reason": "Items currently available in local stock"
}
```

**Response:** `200 OK`

```json
{
  "status": "rejected_by_college"
}
```

### Change Status: Super Admin Approve

**Endpoint:** `POST /api/store/indents/{id}/super_admin_approve/`
**Action:** Super Admin approves and forwards to Central Store.
**Response:** `200 OK`

```json
{
  "status": "approved"
}
```

### Change Status: Super Admin Reject

**Endpoint:** `POST /api/store/indents/{id}/super_admin_reject/`
**Request Payload:**

```json
{
  "rejection_reason": "Not approved for this quarter"
}
```

**Response:** `200 OK`

```json
{
  "status": "rejected_by_super_admin"
}
```

### Delete Store Indent

**Endpoint:** `DELETE /api/store/indents/{id}/`
**Action:** Hard delete of the indent (if permissions allow).
**Response:** `204 No Content`

---

## 2. Procurement Requirement Operations

### Change Status: Submit for Approval

**Endpoint:** `POST /api/store/procurement/requirements/{id}/submit_for_approval/`
**Response:** `200 OK`

```json
{
  "status": "pending_approval"
}
```

### Change Status: Select Quotation

**Endpoint:** `POST /api/store/procurement/requirements/{id}/select_quotation/`
**Request Payload:**

```json
{
  "quotation_id": 123
}
```

**Response:** `200 OK`

```json
{
  "status": "quotation_selected",
  "quotation": 123
}
```

### Delete Procurement Requirement

**Endpoint:** `DELETE /api/store/procurement/requirements/{id}/`
**Response:** `204 No Content`

---

## 3. Material Issue Note (MIN) Operations

### Change Status: Mark Dispatched

**Endpoint:** `POST /api/store/transfers/material-issues/{id}/mark_dispatched/`
**Response:** `200 OK`

```json
{
  "status": "dispatched"
}
```

### Change Status: Confirm Receipt

**Endpoint:** `POST /api/store/transfers/material-issues/{id}/confirm_receipt/`
**Response:** `200 OK`

```json
{
  "status": "received"
}
```

### Delete Material Issue Note

**Endpoint:** `DELETE /api/store/transfers/material-issues/{id}/`
**Response:** `204 No Content`

---

## 4. Bulk Delete (Utility)

Many viewsets in the system support bulk deletion through a standardized endpoint.

**Endpoint:** `POST /api/store/{module}/bulk_delete/`
**Request Payload:**

```json
{
  "ids": [1, 2, 3]
}
```

**Response:** `200 OK`

```json
{
  "message": "3 items deleted successfully",
  "deleted_ids": [1, 2, 3]
}
```

---

## Status Mapping Summary

| Module             | Status Field | Status Choices                                                                                                                                                                               |
| :----------------- | :----------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Store Indent**   | `status`     | `draft`, `submitted`, `pending_college_approval`, `college_approved`, `pending_super_admin`, `super_admin_approved`, `approved`, `partially_fulfilled`, `fulfilled`, `rejected`, `cancelled` |
| **Procurement**    | `status`     | `draft`, `submitted`, `pending_approval`, `approved`, `quotations_received`, `po_created`, `fulfilled`, `cancelled`                                                                          |
| **Material Issue** | `status`     | `prepared`, `dispatched`, `in_transit`, `received`, `cancelled`                                                                                                                              |
