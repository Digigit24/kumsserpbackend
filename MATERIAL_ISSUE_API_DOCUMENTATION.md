# Material Issue Note API Documentation

**Base URL:** `http://127.0.0.1:8000/api/v1/store/`

---

## Overview

Material Issue Note (MIN) APIs manage the lifecycle of material transfers from the central store to colleges. The workflow includes creating, dispatching, and receiving materials with full tracking.

## Status Flow

```
prepared → dispatched → in_transit → received
                    ↓
                cancelled
```

---

## Authentication

All endpoints require authentication via JWT token or session-based authentication.

**Headers Required:**

```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

---

## Endpoints

### 1. List Material Issue Notes

**GET** `/material-issues/`

**Description:** Retrieve a paginated list of all material issue notes. College users see only their college's material issues; central managers see all.

**Query Parameters:**

- `status` (optional): Filter by status (`prepared`, `dispatched`, `in_transit`, `received`, `cancelled`)
- `receiving_college` (optional): Filter by receiving college ID
- `issue_date` (optional): Filter by issue date (YYYY-MM-DD)
- `search` (optional): Search by MIN number
- `ordering` (optional): Sort by field (e.g., `-issue_date`, `min_number`)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of results per page

**Request Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/store/material-issues/?status=dispatched&page=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**

```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/v1/store/material-issues/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "min_number": "MIN-240107-0001",
      "indent": 5,
      "central_store": 1,
      "receiving_college": 3,
      "issue_date": "2024-01-07",
      "issued_by": 10,
      "received_by": null,
      "transport_mode": "Road Transport",
      "vehicle_number": "MH12AB1234",
      "driver_name": "John Doe",
      "driver_contact": "9876543210",
      "status": "dispatched",
      "dispatch_date": "2024-01-07T10:30:00Z",
      "receipt_date": null,
      "min_document": "/media/material_issue_notes/MIN-240107-0001.pdf",
      "internal_notes": "Handle with care",
      "receipt_confirmation_notes": null,
      "created_at": "2024-01-07T09:00:00Z",
      "updated_at": "2024-01-07T10:30:00Z"
    }
  ]
}
```

---

### 2. Retrieve Material Issue Note Details

**GET** `/material-issues/{id}/`

**Description:** Get detailed information about a specific material issue note, including all items.

**URL Parameters:**

- `id` (required): Material Issue Note ID

**Request Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/store/material-issues/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**

```json
{
  "id": 1,
  "min_number": "MIN-240107-0001",
  "indent": 5,
  "central_store": 1,
  "receiving_college": 3,
  "issue_date": "2024-01-07",
  "issued_by": 10,
  "received_by": null,
  "transport_mode": "Road Transport",
  "vehicle_number": "MH12AB1234",
  "driver_name": "John Doe",
  "driver_contact": "9876543210",
  "status": "dispatched",
  "dispatch_date": "2024-01-07T10:30:00Z",
  "receipt_date": null,
  "min_document": "/media/material_issue_notes/MIN-240107-0001.pdf",
  "internal_notes": "Handle with care",
  "receipt_confirmation_notes": null,
  "created_at": "2024-01-07T09:00:00Z",
  "updated_at": "2024-01-07T10:30:00Z",
  "items": [
    {
      "id": 1,
      "material_issue": 1,
      "indent_item": 10,
      "item": 25,
      "issued_quantity": 50,
      "unit": "pcs",
      "batch_number": "BATCH-2024-001",
      "remarks": "Good condition",
      "created_at": "2024-01-07T09:00:00Z",
      "updated_at": "2024-01-07T09:00:00Z"
    },
    {
      "id": 2,
      "material_issue": 1,
      "indent_item": 11,
      "item": 26,
      "issued_quantity": 100,
      "unit": "pcs",
      "batch_number": "BATCH-2024-002",
      "remarks": null,
      "created_at": "2024-01-07T09:00:00Z",
      "updated_at": "2024-01-07T09:00:00Z"
    }
  ]
}
```

---

### 3. Create Material Issue Note

**POST** `/material-issues/`

**Description:** Create a new material issue note. This is typically done by the central store manager after an indent is approved.

**Permission Required:** Central Store Manager

**Request Payload:**

```json
{
  "indent": 5,
  "central_store": 1,
  "receiving_college": 3,
  "issue_date": "2024-01-07",
  "issued_by": 10,
  "transport_mode": "Road Transport",
  "vehicle_number": "MH12AB1234",
  "driver_name": "John Doe",
  "driver_contact": "9876543210",
  "internal_notes": "Handle with care",
  "items": [
    {
      "indent_item": 10,
      "item": 25,
      "issued_quantity": 50,
      "unit": "pcs",
      "batch_number": "BATCH-2024-001",
      "remarks": "Good condition"
    },
    {
      "indent_item": 11,
      "item": 26,
      "issued_quantity": 100,
      "unit": "pcs",
      "batch_number": "BATCH-2024-002"
    }
  ]
}
```

**Field Descriptions:**

- `indent` (integer, required): ID of the approved store indent
- `central_store` (integer, required): ID of the issuing central store
- `receiving_college` (integer, required): ID of the receiving college
- `issue_date` (date, required): Date of material issue (YYYY-MM-DD)
- `issued_by` (integer, optional): ID of user issuing materials (defaults to current user)
- `transport_mode` (string, optional): Mode of transportation
- `vehicle_number` (string, optional): Vehicle registration number
- `driver_name` (string, optional): Driver's name
- `driver_contact` (string, optional): Driver's contact number
- `internal_notes` (string, optional): Internal notes for reference
- `items` (array, optional): List of items being issued
  - `indent_item` (integer, required): ID of the indent item
  - `item` (integer, required): ID of the store item
  - `issued_quantity` (integer, required): Quantity being issued
  - `unit` (string, required): Unit of measurement
  - `batch_number` (string, optional): Batch/lot number
  - `remarks` (string, optional): Item-specific remarks

**Request Example:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/store/material-issues/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "indent": 5,
    "central_store": 1,
    "receiving_college": 3,
    "issue_date": "2024-01-07",
    "transport_mode": "Road Transport",
    "vehicle_number": "MH12AB1234",
    "driver_name": "John Doe",
    "driver_contact": "9876543210",
    "items": [
      {
        "indent_item": 10,
        "item": 25,
        "issued_quantity": 50,
        "unit": "pcs"
      }
    ]
  }'
```

**Response (201 Created):**

```json
{
  "id": 1,
  "min_number": "MIN-240107-0001",
  "indent": 5,
  "central_store": 1,
  "receiving_college": 3,
  "issue_date": "2024-01-07",
  "issued_by": 10,
  "received_by": null,
  "transport_mode": "Road Transport",
  "vehicle_number": "MH12AB1234",
  "driver_name": "John Doe",
  "driver_contact": "9876543210",
  "status": "prepared",
  "dispatch_date": null,
  "receipt_date": null,
  "min_document": null,
  "internal_notes": null,
  "receipt_confirmation_notes": null,
  "created_at": "2024-01-07T09:00:00Z",
  "updated_at": "2024-01-07T09:00:00Z",
  "items": [...]
}
```

**Error Response (400 Bad Request):**

```json
{
  "indent": ["This field is required."],
  "items": [
    {
      "issued_quantity": ["Cannot issue more than approved quantity (30)"]
    }
  ]
}
```

---

### 4. Update Material Issue Note

**PUT** `/material-issues/{id}/` or **PATCH** `/material-issues/{id}/`

**Description:** Update an existing material issue note. Full update with PUT, partial with PATCH.

**Permission Required:** Central Store Manager

**URL Parameters:**

- `id` (required): Material Issue Note ID

**Request Payload (PATCH example - partial update):**

```json
{
  "vehicle_number": "MH12CD5678",
  "driver_name": "Jane Smith",
  "internal_notes": "Updated transport details"
}
```

**Request Example:**

```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/store/material-issues/1/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_number": "MH12CD5678",
    "driver_name": "Jane Smith"
  }'
```

**Response (200 OK):**

```json
{
  "id": 1,
  "min_number": "MIN-240107-0001",
  "indent": 5,
  "central_store": 1,
  "receiving_college": 3,
  "issue_date": "2024-01-07",
  "vehicle_number": "MH12CD5678",
  "driver_name": "Jane Smith",
  "status": "prepared",
  ...
}
```

---

### 5. Delete Material Issue Note

**DELETE** `/material-issues/{id}/`

**Description:** Delete a material issue note (soft delete recommended in production).

**Permission Required:** Central Store Manager

**URL Parameters:**

- `id` (required): Material Issue Note ID

**Request Example:**

```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/store/material-issues/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (204 No Content):**
_(No response body)_

---

### 6. Mark Material Issue as Dispatched

**POST** `/material-issues/{id}/mark_dispatched/`

**Description:** Change status from `prepared` to `dispatched` and record the dispatch timestamp.

**Permission Required:** Central Store Manager

**URL Parameters:**

- `id` (required): Material Issue Note ID

**Request Payload:**

```json
{}
```

**Request Example:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/store/material-issues/1/mark_dispatched/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK):**

```json
{
  "status": "dispatched"
}
```

**Error Response (400 Bad Request):**

```json
{
  "detail": "Cannot dispatch material issue in current status"
}
```

---

### 7. Confirm Receipt of Materials

**POST** `/material-issues/{id}/confirm_receipt/`

**Description:** Confirm that materials have been received at the college. Changes status to `received`, records receipt timestamp, and creates college inventory.

**Permission Required:** College store manager or authorized receiver

**URL Parameters:**

- `id` (required): Material Issue Note ID

**Request Payload:**

```json
{
  "notes": "All materials received in good condition. Verified quantities."
}
```

**Field Descriptions:**

- `notes` (string, optional): Receipt confirmation notes

**Request Example:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/store/material-issues/1/confirm_receipt/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "All materials received in good condition"
  }'
```

**Response (200 OK):**

```json
{
  "status": "received"
}
```

**Error Response (403 Forbidden):**

```json
{
  "detail": "You do not have permission to confirm receipt for this college"
}
```

---

### 8. Generate PDF Document

**POST** `/material-issues/{id}/generate_pdf/`

**Description:** Generate a PDF document for the material issue note.

**Permission Required:** Central Store Manager

**URL Parameters:**

- `id` (required): Material Issue Note ID

**Request Payload:**

```json
{}
```

**Request Example:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/store/material-issues/1/generate_pdf/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response (200 OK):**

```json
{
  "status": "pdf_generated"
}
```

---

## Status Transitions

### Valid Status Transitions

| Current Status | Allowed Next Status | Action/Endpoint                       |
| -------------- | ------------------- | ------------------------------------- |
| `prepared`     | `dispatched`        | POST `/mark_dispatched/`              |
| `prepared`     | `cancelled`         | PATCH with `{"status": "cancelled"}`  |
| `dispatched`   | `in_transit`        | PATCH with `{"status": "in_transit"}` |
| `dispatched`   | `received`          | POST `/confirm_receipt/`              |
| `in_transit`   | `received`          | POST `/confirm_receipt/`              |

### Status PATCH Examples

#### 1. Mark as In Transit

**PATCH** `/material-issues/{id}/`

```json
{
  "status": "in_transit"
}
```

**Request:**

```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/store/material-issues/1/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_transit"}'
```

**Response (200 OK):**

```json
{
  "id": 1,
  "min_number": "MIN-240107-0001",
  "status": "in_transit",
  "dispatch_date": "2024-01-07T10:30:00Z",
  ...
}
```

#### 2. Cancel Material Issue

**PATCH** `/material-issues/{id}/`

```json
{
  "status": "cancelled",
  "internal_notes": "Cancelled due to indent revision"
}
```

**Request:**

```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/store/material-issues/1/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "cancelled",
    "internal_notes": "Cancelled due to indent revision"
  }'
```

**Response (200 OK):**

```json
{
  "id": 1,
  "min_number": "MIN-240107-0001",
  "status": "cancelled",
  "internal_notes": "Cancelled due to indent revision",
  ...
}
```

---

## Alternative Workflow: Create MIN via Indent

You can also create a Material Issue Note directly from an approved indent using the indent's `issue_materials` action.

**POST** `/indents/{indent_id}/issue_materials/`

**Request Payload:**

```json
{
  "issue_date": "2024-01-07",
  "transport_mode": "Road Transport",
  "vehicle_number": "MH12AB1234",
  "driver_name": "John Doe",
  "driver_contact": "9876543210",
  "items": [
    {
      "indent_item": 10,
      "item": 25,
      "issued_quantity": 50,
      "unit": "pcs"
    }
  ]
}
```

**Response:** Same as Create Material Issue Note (returns MaterialIssueNoteDetailSerializer)

---

## Field Validations & Business Rules

### 1. Creation Validations

- **Indent must be approved:** Only indents with status `super_admin_approved` or `approved` can have materials issued
- **Issued quantity cannot exceed approved quantity:** Each item's `issued_quantity` must be ≤ `indent_item.approved_quantity`
- **Central store must have sufficient stock:** Inventory checks are performed on creation

### 2. Status Change Validations

- **Prepared → Dispatched:** Only central store managers can dispatch
- **Dispatched/In Transit → Received:** Only college users (college_admin or store managers) from the receiving college can confirm receipt
- **Cannot modify after received:** Once status is `received`, changes are restricted

### 3. Inventory Impact

- **On Dispatch:** Central store inventory is reduced by issued quantities
- **On Receipt:** College store inventory is created/increased by issued quantities

---

## Error Codes

| Status Code | Meaning      | Example                              |
| ----------- | ------------ | ------------------------------------ |
| 200         | Success      | Successful GET/PATCH/PUT             |
| 201         | Created      | Successfully created MIN             |
| 204         | No Content   | Successfully deleted MIN             |
| 400         | Bad Request  | Validation failed, invalid payload   |
| 401         | Unauthorized | Missing or invalid authentication    |
| 403         | Forbidden    | User lacks permission for action     |
| 404         | Not Found    | Material Issue Note ID doesn't exist |
| 500         | Server Error | Internal server error                |

---

## Common Error Examples

### Insufficient Stock

```json
{
  "items": [
    {
      "issued_quantity": ["Insufficient stock. Available: 20, Requested: 50"]
    }
  ]
}
```

### Invalid Status Transition

```json
{
  "detail": "Cannot confirm receipt. Material issue is not in dispatched or in_transit status."
}
```

### Permission Denied

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Indent Not Approved

```json
{
  "detail": "Indent must be approved by super admin before issuing materials"
}
```

---

## Testing Examples

### Using Python requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/store"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# List all material issues
response = requests.get(f"{BASE_URL}/material-issues/", headers=headers)
print(response.json())

# Get specific material issue
response = requests.get(f"{BASE_URL}/material-issues/1/", headers=headers)
print(response.json())

# Mark as dispatched
response = requests.post(
    f"{BASE_URL}/material-issues/1/mark_dispatched/",
    headers=headers,
    json={}
)
print(response.json())

# Confirm receipt
response = requests.post(
    f"{BASE_URL}/material-issues/1/confirm_receipt/",
    headers=headers,
    json={"notes": "All items received in good condition"}
)
print(response.json())

# Update status to in_transit
response = requests.patch(
    f"{BASE_URL}/material-issues/1/",
    headers=headers,
    json={"status": "in_transit"}
)
print(response.json())
```

### Using curl

```bash
# List all material issues with filters
curl -X GET "http://127.0.0.1:8000/api/v1/store/material-issues/?status=dispatched&receiving_college=3" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create new material issue
curl -X POST "http://127.0.0.1:8000/api/v1/store/material-issues/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @material_issue_payload.json

# Update status to in_transit
curl -X PATCH "http://127.0.0.1:8000/api/v1/store/material-issues/1/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_transit"}'

# Mark as dispatched
curl -X POST "http://127.0.0.1:8000/api/v1/store/material-issues/1/mark_dispatched/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Confirm receipt
curl -X POST "http://127.0.0.1:8000/api/v1/store/material-issues/1/confirm_receipt/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Materials received and verified"}'
```

---

## Related Models & Endpoints

### Related to Material Issue:

- **Store Indent:** `/api/v1/store/indents/` - Source indent for material issue
- **Central Store:** `/api/v1/store/central-stores/` - Issuing store
- **College:** `/api/v1/core/colleges/` - Receiving college
- **Store Items:** `/api/v1/store/items/` - Items being issued
- **Central Store Inventory:** `/api/v1/store/central-inventory/` - Inventory tracking

---

## Notes

1. All timestamps are in ISO 8601 format with UTC timezone (`2024-01-07T10:30:00Z`)
2. Date fields use `YYYY-MM-DD` format
3. The system automatically generates unique MIN numbers using the pattern `MIN-YYMMDD-XXXX`
4. File uploads (PDF documents) are stored in `media/material_issue_notes/`
5. Pagination is enabled by default with page size of 20 (configurable)
6. Filtering supports exact match and range queries depending on field type

---

**Last Updated:** 2024-01-07
