# Store Module: Procurement & Transfers API Documentation

**Version:** 1.0
**Last Updated:** 2026-01-06
**Base URL:** `/api/store/`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Headers](#common-headers)
4. [Error Handling](#error-handling)
5. [Procurement Module](#procurement-module)
6. [Transfers Module](#transfers-module)
7. [Status Flow Diagrams](#status-flow-diagrams)
8. [Permissions](#permissions)
9. [Dependencies](#dependencies)

---

## Overview

This document provides comprehensive API documentation for the **Procurement** and **Transfers** modules within the Store application. These modules handle:

- **Procurement**: Managing procurement requirements, supplier quotations, purchase orders, goods receipts, and inventory management
- **Transfers**: Managing store indents (requests) from colleges to central store and material issue notes

---

## Authentication

The API uses **Token-Based Authentication** (Django REST Framework Token Authentication).

### Authentication Methods

1. **Token Authentication** (Primary)
2. **Session Authentication** (Fallback)

### Getting a Token

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "key": "your_auth_token_here",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com",
    "user_type": "super_admin",
    "college_id": 1
  }
}
```

---

## Common Headers

Include these headers in **all API requests**:

```http
Authorization: Token your_auth_token_here
Content-Type: application/json
Accept: application/json
```

### Optional Headers

```http
X-College-ID: 1  # For multi-college scoping (if applicable)
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message description",
  "errors": {
    "field_name": ["Error message for this field"]
  }
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Validation error or bad request
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Common Error Scenarios

**Authentication Error:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Permission Denied:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Validation Error:**
```json
{
  "quantity": ["This field is required."],
  "unit_price": ["Ensure this value is greater than or equal to 0."]
}
```

---

## Procurement Module

The Procurement module manages the complete procurement lifecycle from requirement creation to goods receipt and inventory posting.

### Workflow Overview

```
1. ProcurementRequirement (draft → submitted → pending_approval → approved)
2. SupplierQuotation (multiple suppliers submit quotations)
3. Select Best Quotation (mark_selected)
4. PurchaseOrder (draft → sent → acknowledged → partially_received → fulfilled)
5. GoodsReceiptNote (received → pending_inspection → inspected → approved → posted_to_inventory)
6. InspectionNote (quality check)
7. CentralStoreInventory (automatically updated)
```

---

### 1. Procurement Requirement

**Purpose:** Create and manage procurement requirements for items needed by the central store.

#### List Procurement Requirements

**Endpoint:** `GET /api/store/procurement/requirements/`

**Headers:**
```http
Authorization: Token your_token
Content-Type: application/json
```

**Query Parameters:**
- `status` - Filter by status: `draft`, `submitted`, `pending_approval`, `approved`, `quotations_received`, `po_created`, `fulfilled`, `cancelled`
- `urgency` - Filter by urgency: `low`, `medium`, `high`, `urgent`
- `requirement_date` - Filter by requirement date
- `search` - Search by requirement_number or title
- `ordering` - Order by: `requirement_date`, `-requirement_date`, `required_by_date`, `created_at`
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Response:**
```json
{
  "count": 25,
  "next": "http://example.com/api/store/procurement/requirements/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "requirement_number": "REQ-2026-0001",
      "title": "Office Supplies Q1 2026",
      "status": "approved",
      "urgency": "medium",
      "requirement_date": "2026-01-05",
      "required_by_date": "2026-02-01",
      "central_store": 1
    }
  ]
}
```

#### Get Procurement Requirement Detail

**Endpoint:** `GET /api/store/procurement/requirements/{id}/`

**Response:**
```json
{
  "id": 1,
  "requirement_number": "REQ-2026-0001",
  "central_store": 1,
  "title": "Office Supplies Q1 2026",
  "description": "Procurement of essential office supplies",
  "requirement_date": "2026-01-05",
  "required_by_date": "2026-02-01",
  "urgency": "medium",
  "status": "approved",
  "approval_request": 5,
  "estimated_budget": "150000.00",
  "justification": "Required for operational needs",
  "metadata": {},
  "items": [
    {
      "id": 1,
      "requirement": 1,
      "item_description": "A4 Paper Reams",
      "category": 2,
      "quantity": 100,
      "unit": "ream",
      "estimated_unit_price": "250.00",
      "estimated_total": "25000.00",
      "specifications": "80 GSM white paper",
      "remarks": null,
      "created_at": "2026-01-05T10:00:00Z",
      "updated_at": "2026-01-05T10:00:00Z"
    }
  ],
  "quotations_count": 3,
  "created_at": "2026-01-05T10:00:00Z",
  "updated_at": "2026-01-05T12:30:00Z"
}
```

#### Create Procurement Requirement

**Endpoint:** `POST /api/store/procurement/requirements/`

**Permission:** Authenticated users (Super Admin or Central Store Manager)

**Request:**
```json
{
  "central_store": 1,
  "title": "Office Supplies Q1 2026",
  "description": "Procurement of essential office supplies",
  "required_by_date": "2026-02-01",
  "urgency": "medium",
  "estimated_budget": "150000.00",
  "justification": "Required for operational needs",
  "items": [
    {
      "item_description": "A4 Paper Reams",
      "category": 2,
      "quantity": 100,
      "unit": "ream",
      "estimated_unit_price": "250.00",
      "specifications": "80 GSM white paper"
    },
    {
      "item_description": "Ball Point Pens",
      "category": 2,
      "quantity": 500,
      "unit": "piece",
      "estimated_unit_price": "5.00",
      "specifications": "Blue ink"
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "requirement_number": "REQ-2026-0001",
  "central_store": 1,
  "title": "Office Supplies Q1 2026",
  "description": "Procurement of essential office supplies",
  "requirement_date": "2026-01-05",
  "required_by_date": "2026-02-01",
  "urgency": "medium",
  "status": "submitted",
  "approval_request": null,
  "estimated_budget": "150000.00",
  "justification": "Required for operational needs",
  "metadata": {},
  "created_at": "2026-01-05T10:00:00Z",
  "updated_at": "2026-01-05T10:00:00Z"
}
```

**Important Notes:**
- `requirement_number` is auto-generated
- Status starts as `draft` and automatically transitions to `submitted`
- An approval request is automatically created when status changes to `submitted`

#### Submit for Approval

**Endpoint:** `POST /api/store/procurement/requirements/{id}/submit_for_approval/`

**Permission:** Authenticated users

**Response:**
```json
{
  "status": "pending_approval"
}
```

#### Get Quotations for Requirement

**Endpoint:** `GET /api/store/procurement/requirements/{id}/quotations/`

**Response:**
```json
[
  {
    "id": 1,
    "quotation_number": "QUOT-2026-0001",
    "requirement": 1,
    "supplier": 3,
    "quotation_date": "2026-01-10",
    "status": "accepted",
    "is_selected": true
  },
  {
    "id": 2,
    "quotation_number": "QUOT-2026-0002",
    "requirement": 1,
    "supplier": 4,
    "quotation_date": "2026-01-11",
    "status": "rejected",
    "is_selected": false
  }
]
```

#### Compare Quotations

**Endpoint:** `GET /api/store/procurement/requirements/{id}/compare_quotations/`

**Permission:** Authenticated users

**Response:**
```json
[
  {
    "quotation": {
      "id": 1,
      "quotation_number": "QUOT-2026-0001",
      "requirement": 1,
      "supplier": 3,
      "quotation_date": "2026-01-10",
      "supplier_reference_number": "SUPP-REF-001",
      "valid_until": "2026-02-10",
      "total_amount": "148500.00",
      "tax_amount": "26730.00",
      "grand_total": "175230.00",
      "payment_terms": "30 days",
      "delivery_time_days": 15,
      "warranty_terms": "6 months warranty",
      "status": "accepted",
      "is_selected": true,
      "items": [
        {
          "id": 1,
          "item_description": "A4 Paper Reams",
          "quantity": 100,
          "unit": "ream",
          "unit_price": "245.00",
          "tax_rate": "18.00",
          "tax_amount": "4410.00",
          "total_amount": "28910.00",
          "brand": "JK Paper"
        }
      ]
    },
    "supplier": {
      "id": 3,
      "supplier_code": "SUP-001",
      "name": "ABC Stationers Pvt Ltd",
      "rating": 4,
      "supplier_type": "wholesaler"
    }
  }
]
```

#### Select Quotation

**Endpoint:** `POST /api/store/procurement/requirements/{id}/select_quotation/`

**Permission:** IsCEOOrFinance (CEO or Finance group members, or Super Admin)

**Request:**
```json
{
  "quotation_id": 1
}
```

**Response:**
```json
{
  "status": "quotation_selected",
  "quotation": 1
}
```

**Side Effects:**
- Selected quotation status → `accepted`, `is_selected` → `true`
- All other quotations for this requirement → `rejected`, `is_selected` → `false`
- Requirement status → `approved`

---

### 2. Supplier Quotation

**Purpose:** Manage quotations received from suppliers in response to procurement requirements.

#### List Supplier Quotations

**Endpoint:** `GET /api/store/procurement/quotations/`

**Query Parameters:**
- `requirement` - Filter by requirement ID
- `supplier` - Filter by supplier ID
- `status` - Filter by status: `received`, `under_review`, `accepted`, `rejected`
- `is_selected` - Filter by selection: `true`, `false`
- `search` - Search by quotation_number
- `ordering` - Order by: `quotation_date`, `-quotation_date`, `created_at`

**Response:**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "quotation_number": "QUOT-2026-0001",
      "requirement": 1,
      "supplier": 3,
      "quotation_date": "2026-01-10",
      "status": "accepted",
      "is_selected": true
    }
  ]
}
```

#### Get Quotation Detail

**Endpoint:** `GET /api/store/procurement/quotations/{id}/`

**Response:**
```json
{
  "id": 1,
  "quotation_number": "QUOT-2026-0001",
  "requirement": 1,
  "supplier": 3,
  "quotation_date": "2026-01-10",
  "supplier_reference_number": "SUPP-REF-001",
  "valid_until": "2026-02-10",
  "total_amount": "148500.00",
  "tax_amount": "26730.00",
  "grand_total": "175230.00",
  "payment_terms": "30 days",
  "delivery_time_days": 15,
  "warranty_terms": "6 months warranty",
  "quotation_file": "https://s3.amazonaws.com/bucket/quotations/file.pdf",
  "status": "accepted",
  "is_selected": true,
  "rejection_reason": null,
  "notes": "Competitive pricing",
  "supplier_details": {
    "id": 3,
    "supplier_code": "SUP-001",
    "name": "ABC Stationers Pvt Ltd",
    "contact_person": "John Doe",
    "email": "john@abcstationers.com",
    "phone": "+91-9876543210",
    "rating": 4,
    "supplier_type": "wholesaler"
  },
  "items": [
    {
      "id": 1,
      "quotation": 1,
      "requirement_item": 1,
      "item_description": "A4 Paper Reams",
      "quantity": 100,
      "unit": "ream",
      "unit_price": "245.00",
      "tax_rate": "18.00",
      "tax_amount": "4410.00",
      "total_amount": "28910.00",
      "specifications": "80 GSM white paper",
      "brand": "JK Paper",
      "hsn_code": "4802"
    }
  ],
  "created_at": "2026-01-10T09:00:00Z",
  "updated_at": "2026-01-10T09:00:00Z"
}
```

#### Create Supplier Quotation

**Endpoint:** `POST /api/store/procurement/quotations/`

**Permission:** IsCentralStoreManager (Super Admin only)

**Request:**
```json
{
  "quotation_file": "base64_encoded_pdf_or_file_upload"
}
```

**Note:** This endpoint only accepts file upload. The quotation details are extracted from the uploaded file.

**Response:** `201 Created`

#### Mark Quotation as Selected

**Endpoint:** `POST /api/store/procurement/quotations/{id}/mark_selected/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "selected"
}
```

**Validation:**
- Requirement must be in `approved` or `quotations_received` status
- Cannot select quotation for cancelled/fulfilled requirement

---

### 3. Purchase Order

**Purpose:** Create and manage purchase orders based on selected quotations.

#### List Purchase Orders

**Endpoint:** `GET /api/store/procurement/purchase-orders/`

**Query Parameters:**
- `status` - Filter by status: `draft`, `sent`, `acknowledged`, `partially_received`, `fulfilled`, `cancelled`
- `supplier` - Filter by supplier ID
- `po_date` - Filter by PO date
- `search` - Search by po_number
- `ordering` - Order by: `po_date`, `-po_date`, `created_at`

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "po_number": "PO-2026-0001",
      "supplier": 3,
      "status": "acknowledged",
      "po_date": "2026-01-12",
      "expected_delivery_date": "2026-01-27"
    }
  ]
}
```

#### Get Purchase Order Detail

**Endpoint:** `GET /api/store/procurement/purchase-orders/{id}/`

**Response:**
```json
{
  "id": 1,
  "po_number": "PO-2026-0001",
  "requirement": 1,
  "quotation": 1,
  "supplier": 3,
  "central_store": 1,
  "po_date": "2026-01-12",
  "expected_delivery_date": "2026-01-27",
  "delivery_address_line1": "Central Store Building",
  "delivery_address_line2": "Campus Road",
  "delivery_city": "Mumbai",
  "delivery_state": "Maharashtra",
  "delivery_pincode": "400001",
  "total_amount": "148500.00",
  "tax_amount": "26730.00",
  "grand_total": "175230.00",
  "payment_terms": "30 days from delivery",
  "delivery_terms": "Ex-warehouse",
  "special_instructions": "Handle with care",
  "terms_and_conditions": "Standard T&C apply",
  "status": "acknowledged",
  "po_document": "https://s3.amazonaws.com/bucket/purchase_orders/PO-2026-0001.pdf",
  "sent_date": "2026-01-12T14:00:00Z",
  "acknowledged_date": "2026-01-13T10:30:00Z",
  "completed_date": null,
  "supplier_details": {
    "id": 3,
    "supplier_code": "SUP-001",
    "name": "ABC Stationers Pvt Ltd",
    "contact_person": "John Doe",
    "email": "john@abcstationers.com",
    "phone": "+91-9876543210"
  },
  "items": [
    {
      "id": 1,
      "purchase_order": 1,
      "quotation_item": 1,
      "item_description": "A4 Paper Reams",
      "hsn_code": "4802",
      "quantity": 100,
      "unit": "ream",
      "unit_price": "245.00",
      "tax_rate": "18.00",
      "tax_amount": "4410.00",
      "total_amount": "28910.00",
      "received_quantity": 50,
      "pending_quantity": 50,
      "specifications": "80 GSM white paper"
    }
  ],
  "created_at": "2026-01-12T10:00:00Z",
  "updated_at": "2026-01-13T10:30:00Z"
}
```

#### Create Purchase Order

**Endpoint:** `POST /api/store/procurement/purchase-orders/`

**Permission:** IsCentralStoreManager

**Request:**
```json
{
  "requirement": 1,
  "quotation": 1,
  "supplier": 3,
  "central_store": 1,
  "po_date": "2026-01-12",
  "expected_delivery_date": "2026-01-27",
  "delivery_address_line1": "Central Store Building",
  "delivery_address_line2": "Campus Road",
  "delivery_city": "Mumbai",
  "delivery_state": "Maharashtra",
  "delivery_pincode": "400001",
  "total_amount": "148500.00",
  "tax_amount": "26730.00",
  "grand_total": "175230.00",
  "payment_terms": "30 days from delivery",
  "delivery_terms": "Ex-warehouse",
  "special_instructions": "Handle with care",
  "terms_and_conditions": "Standard T&C apply",
  "items": [
    {
      "quotation_item": 1,
      "item_description": "A4 Paper Reams",
      "hsn_code": "4802",
      "quantity": 100,
      "unit": "ream",
      "unit_price": "245.00",
      "tax_rate": "18.00",
      "tax_amount": "4410.00",
      "total_amount": "28910.00",
      "specifications": "80 GSM white paper"
    }
  ]
}
```

**Response:** `201 Created`

**Validation:**
- PO total must match quotation total within 2% tolerance
- Cannot create PO without approved requirement
- Requirement status automatically updated to `po_created`

#### Generate PO PDF

**Endpoint:** `POST /api/store/procurement/purchase-orders/{id}/generate_pdf/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "pdf_generated"
}
```

#### Send to Supplier

**Endpoint:** `POST /api/store/procurement/purchase-orders/{id}/send_to_supplier/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "sent"
}
```

**Side Effects:**
- Status → `sent`
- `sent_date` → current timestamp

#### Acknowledge PO

**Endpoint:** `POST /api/store/procurement/purchase-orders/{id}/acknowledge/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "acknowledged"
}
```

**Side Effects:**
- Status → `acknowledged`
- `acknowledged_date` → current timestamp

---

### 4. Goods Receipt Note (GRN)

**Purpose:** Record receipt of goods from suppliers and manage quality inspection.

#### List Goods Receipt Notes

**Endpoint:** `GET /api/store/procurement/goods-receipts/`

**Query Parameters:**
- `purchase_order` - Filter by purchase order ID
- `status` - Filter by status: `received`, `pending_inspection`, `inspected`, `approved`, `rejected`, `posted_to_inventory`
- `receipt_date` - Filter by receipt date
- `search` - Search by grn_number

**Response:**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "grn_number": "GRN-2026-0001",
      "purchase_order": 1,
      "status": "posted_to_inventory",
      "receipt_date": "2026-01-25"
    }
  ]
}
```

#### Get GRN Detail

**Endpoint:** `GET /api/store/procurement/goods-receipts/{id}/`

**Response:**
```json
{
  "id": 1,
  "grn_number": "GRN-2026-0001",
  "purchase_order": 1,
  "supplier": 3,
  "central_store": 1,
  "receipt_date": "2026-01-25",
  "invoice_number": "INV-2026-001",
  "invoice_date": "2026-01-24",
  "invoice_amount": "175230.00",
  "invoice_file": "https://s3.amazonaws.com/bucket/grn_invoices/invoice.pdf",
  "delivery_challan_number": "DC-001",
  "delivery_challan_file": "https://s3.amazonaws.com/bucket/grn_challans/challan.pdf",
  "lr_number": "LR-12345",
  "lr_copy": "https://s3.amazonaws.com/bucket/grn_lr/lr.pdf",
  "vehicle_number": "MH-01-AB-1234",
  "transporter_name": "Express Logistics",
  "received_by": 5,
  "status": "posted_to_inventory",
  "inspection_approval_request": null,
  "posted_to_inventory_date": "2026-01-26T10:00:00Z",
  "remarks": "All items received in good condition",
  "inspection": 1,
  "items": [
    {
      "id": 1,
      "grn": 1,
      "po_item": 1,
      "item_description": "A4 Paper Reams",
      "ordered_quantity": 100,
      "received_quantity": 100,
      "accepted_quantity": 98,
      "rejected_quantity": 2,
      "unit": "ream",
      "batch_number": "BATCH-2026-01",
      "serial_number": null,
      "manufacturing_date": "2025-12-15",
      "expiry_date": null,
      "rejection_reason": "2 reams damaged packaging",
      "inspection_notes": "Overall quality good",
      "quality_status": "passed"
    }
  ],
  "created_at": "2026-01-25T14:00:00Z",
  "updated_at": "2026-01-26T10:00:00Z"
}
```

#### Create GRN

**Endpoint:** `POST /api/store/procurement/goods-receipts/`

**Permission:** IsCentralStoreManager

**Request:**
```json
{
  "purchase_order": 1,
  "supplier": 3,
  "central_store": 1,
  "receipt_date": "2026-01-25",
  "invoice_number": "INV-2026-001",
  "invoice_date": "2026-01-24",
  "invoice_amount": "175230.00",
  "invoice_file": "file_upload_or_base64",
  "delivery_challan_number": "DC-001",
  "delivery_challan_file": "file_upload_or_base64",
  "lr_number": "LR-12345",
  "lr_copy": "file_upload_or_base64",
  "vehicle_number": "MH-01-AB-1234",
  "transporter_name": "Express Logistics",
  "received_by": 5,
  "remarks": "All items received in good condition",
  "items": [
    {
      "po_item": 1,
      "item_description": "A4 Paper Reams",
      "ordered_quantity": 100,
      "received_quantity": 100,
      "accepted_quantity": 98,
      "rejected_quantity": 2,
      "unit": "ream",
      "batch_number": "BATCH-2026-01",
      "manufacturing_date": "2025-12-15",
      "rejection_reason": "2 reams damaged packaging",
      "inspection_notes": "Overall quality good",
      "quality_status": "pending"
    }
  ]
}
```

**Response:** `201 Created`

**Validation:**
- Accepted + Rejected must equal Received quantity
- Cannot receive quantity > ordered quantity
- Invoice amount warning if differs from PO by >5%

#### Submit for Inspection

**Endpoint:** `POST /api/store/procurement/goods-receipts/{id}/submit_for_inspection/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "pending_inspection"
}
```

#### Post to Inventory

**Endpoint:** `POST /api/store/procurement/goods-receipts/{id}/post_to_inventory/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "posted_to_inventory"
}
```

**Validation:**
- Cannot post without inspection approval (status must be `approved` or `inspected`)

**Side Effects (Signal-based):**
1. Update PurchaseOrderItem `received_quantity`
2. Update/Create CentralStoreInventory
3. Create InventoryTransaction (type: `receipt`)
4. Create StockReceive record (legacy compatibility)
5. Check PO fulfillment status
6. Generate GRN PDF
7. Set `posted_to_inventory_date` → current timestamp

---

### 5. Inspection Note

**Purpose:** Record quality inspection results for received goods.

#### List Inspection Notes

**Endpoint:** `GET /api/store/procurement/inspections/`

**Query Parameters:**
- `overall_status` - Filter by status: `passed`, `failed`, `partial`, `pending`
- `ordering` - Order by: `inspection_date`, `-inspection_date`

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "grn": 1,
      "inspector": 6,
      "inspection_date": "2026-01-25",
      "overall_status": "passed",
      "quality_rating": 4,
      "packaging_condition": "good",
      "remarks": "All items meet quality standards",
      "recommendation": "accept",
      "inspection_images": []
    }
  ]
}
```

#### Get Inspection Note Detail

**Endpoint:** `GET /api/store/procurement/inspections/{id}/`

**Response:**
```json
{
  "id": 1,
  "grn": 1,
  "inspector": 6,
  "inspection_date": "2026-01-25",
  "overall_status": "passed",
  "quality_rating": 4,
  "packaging_condition": "good",
  "remarks": "All items meet quality standards",
  "recommendation": "accept",
  "inspection_images": [
    "https://s3.amazonaws.com/bucket/inspections/img1.jpg",
    "https://s3.amazonaws.com/bucket/inspections/img2.jpg"
  ],
  "created_at": "2026-01-25T16:00:00Z",
  "updated_at": "2026-01-25T16:00:00Z"
}
```

#### Create Inspection Note

**Endpoint:** `POST /api/store/procurement/inspections/`

**Permission:** IsCentralStoreManager

**Request:**
```json
{
  "grn": 1,
  "inspector": 6,
  "inspection_date": "2026-01-25",
  "overall_status": "passed",
  "quality_rating": 4,
  "packaging_condition": "good",
  "remarks": "All items meet quality standards",
  "recommendation": "accept",
  "inspection_images": []
}
```

**Response:** `201 Created`

**Field Options:**
- `overall_status`: `passed`, `failed`, `partial`, `pending`
- `quality_rating`: 1-5
- `packaging_condition`: `excellent`, `good`, `fair`, `poor`
- `recommendation`: `accept`, `reject`, `partial_accept`

---

### 6. Central Store Inventory

**Purpose:** Track inventory levels at the central store.

#### List Inventory

**Endpoint:** `GET /api/store/central-inventory/`

**Query Parameters:**
- `central_store` - Filter by central store ID
- `item` - Filter by item ID
- `quantity_available` - Filter by available quantity
- `ordering` - Order by: `quantity_available`, `updated_at`

**Response:**
```json
{
  "count": 50,
  "next": "http://example.com/api/store/central-inventory/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "item": 15,
      "item_display": "A4 Paper Reams",
      "central_store": 1,
      "quantity_on_hand": 500,
      "quantity_allocated": 100,
      "quantity_available": 400,
      "min_stock_level": 50,
      "reorder_point": 100,
      "max_stock_level": 1000,
      "last_stock_update": "2026-01-26T10:00:00Z",
      "unit_cost": "245.00",
      "is_active": true,
      "created_at": "2026-01-10T10:00:00Z",
      "updated_at": "2026-01-26T10:00:00Z"
    }
  ]
}
```

#### Get Inventory Detail

**Endpoint:** `GET /api/store/central-inventory/{id}/`

**Response:**
```json
{
  "id": 1,
  "item": 15,
  "item_display": "A4 Paper Reams",
  "central_store": 1,
  "quantity_on_hand": 500,
  "quantity_allocated": 100,
  "quantity_available": 400,
  "min_stock_level": 50,
  "reorder_point": 100,
  "max_stock_level": 1000,
  "last_stock_update": "2026-01-26T10:00:00Z",
  "unit_cost": "245.00",
  "is_active": true,
  "created_at": "2026-01-10T10:00:00Z",
  "updated_at": "2026-01-26T10:00:00Z"
}
```

#### Create Inventory Item

**Endpoint:** `POST /api/store/central-inventory/`

**Permission:** Super Admin only

**Request:**
```json
{
  "item_name": "A4 Paper Reams",
  "central_store": 1,
  "quantity_on_hand": 500,
  "quantity_allocated": 0,
  "quantity_available": 500,
  "min_stock_level": 50,
  "reorder_point": 100,
  "max_stock_level": 1000,
  "unit_cost": "245.00"
}
```

**Note:** This endpoint accepts `item_name` instead of `item` ID. It will find or create the item automatically.

**Response:** `201 Created`

#### Get Low Stock Items

**Endpoint:** `GET /api/store/central-inventory/low_stock/`

**Response:**
```json
[
  {
    "id": 5,
    "item": 20,
    "item_display": "Marker Pens",
    "central_store": 1,
    "quantity_on_hand": 45,
    "quantity_allocated": 10,
    "quantity_available": 35,
    "min_stock_level": 50,
    "reorder_point": 100,
    "unit_cost": "15.00"
  }
]
```

**Note:** Returns items where `quantity_available` <= `reorder_point`

#### Adjust Stock

**Endpoint:** `POST /api/store/central-inventory/{id}/adjust_stock/`

**Permission:** IsCentralStoreManager

**Request:**
```json
{
  "delta": 50,
  "remarks": "Manual adjustment - stock reconciliation"
}
```

**Response:**
```json
{
  "quantity_on_hand": 550,
  "quantity_available": 450,
  "reason": "Manual adjustment - stock reconciliation"
}
```

**Note:**
- Positive `delta` increases stock
- Negative `delta` decreases stock
- Creates an InventoryTransaction with type `adjustment`

---

### 7. Inventory Transaction

**Purpose:** Track all inventory movements (read-only).

#### List Transactions

**Endpoint:** `GET /api/store/inventory-transactions/`

**Query Parameters:**
- `transaction_type` - Filter by type: `receipt`, `issue`, `adjustment`, `transfer`, `return`, `damage`, `write_off`
- `transaction_date` - Filter by date
- `item` - Filter by item ID
- `central_store` - Filter by central store ID
- `search` - Search by transaction_number

**Response:**
```json
{
  "count": 100,
  "next": "http://example.com/api/store/inventory-transactions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "transaction_number": "TRN-2026-0001",
      "transaction_type": "receipt",
      "central_store": 1,
      "item": 15,
      "quantity": 100,
      "transaction_date": "2026-01-26T10:00:00Z",
      "before_quantity": 400,
      "after_quantity": 500,
      "unit_cost": "245.00",
      "total_value": "24500.00",
      "reference_type": 25,
      "reference_id": 1,
      "performed_by": 5,
      "remarks": null,
      "created_at": "2026-01-26T10:00:00Z",
      "updated_at": "2026-01-26T10:00:00Z"
    }
  ]
}
```

#### Get Transaction Detail

**Endpoint:** `GET /api/store/inventory-transactions/{id}/`

**Response:** Same as list item

**Note:** This is a read-only resource. Transactions are automatically created by the system.

---

## Transfers Module

The Transfers module manages the flow of materials from the central store to individual college stores through indents and material issue notes.

### Workflow Overview

```
1. StoreIndent (draft → submitted → pending_college_approval → college_approved → pending_super_admin → super_admin_approved)
2. MaterialIssueNote (prepared → dispatched → in_transit → received)
3. College Inventory Updated (automatically)
```

---

### 1. Store Indent

**Purpose:** College stores request items from the central store.

#### List Store Indents

**Endpoint:** `GET /api/store/indents/`

**Headers:**
```http
Authorization: Token your_token
Content-Type: application/json
X-College-ID: 1  # Optional, for filtering
```

**Query Parameters:**
- `status` - Filter by status
- `college` - Filter by college ID
- `priority` - Filter by priority: `low`, `medium`, `high`, `urgent`
- `indent_date` - Filter by indent date
- `search` - Search by indent_number
- `ordering` - Order by: `indent_date`, `-indent_date`, `created_at`

**Status Values:**
- `draft` - Initial state
- `submitted` - Submitted by college store manager
- `pending_college_approval` - Waiting for college admin approval
- `college_approved` - Approved by college admin
- `pending_super_admin` - Waiting for super admin approval
- `super_admin_approved` - Approved by super admin, ready for issue
- `approved` - Legacy status (same as super_admin_approved)
- `partially_fulfilled` - Some items issued
- `fulfilled` - All items issued
- `rejected_by_college` - Rejected by college admin
- `rejected_by_super_admin` - Rejected by super admin
- `rejected` - Legacy rejected status
- `cancelled` - Cancelled

**Response:**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "indent_number": "IND-2026-0001",
      "college": 2,
      "college_name": "Engineering College Mumbai",
      "central_store": 1,
      "central_store_name": "Main Central Store",
      "status": "super_admin_approved",
      "status_display": "Super Admin Approved",
      "priority": "high",
      "indent_date": "2026-01-20"
    }
  ]
}
```

#### Get Indent Detail

**Endpoint:** `GET /api/store/indents/{id}/`

**Response:**
```json
{
  "id": 1,
  "indent_number": "IND-2026-0001",
  "college": 2,
  "college_name": "Engineering College Mumbai",
  "requesting_store_manager": 10,
  "requesting_store_manager_name": "Rajesh Kumar",
  "central_store": 1,
  "central_store_name": "Main Central Store",
  "indent_date": "2026-01-20",
  "required_by_date": "2026-02-05",
  "priority": "high",
  "justification": "Required for new semester laboratory setup",
  "status": "super_admin_approved",
  "status_display": "Super Admin Approved",
  "approval_request": null,
  "approved_by": 3,
  "approved_by_name": "Admin User",
  "approved_date": "2026-01-22T11:00:00Z",
  "rejection_reason": null,
  "attachments": null,
  "remarks": "Urgent requirement",
  "items": [
    {
      "id": 1,
      "indent": 1,
      "central_store_item": 15,
      "requested_quantity": 50,
      "approved_quantity": 50,
      "issued_quantity": 50,
      "pending_quantity": 0,
      "unit": "ream",
      "justification": "Lab consumables",
      "remarks": null,
      "available_stock_in_central": 400,
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-23T14:00:00Z"
    }
  ],
  "is_active": true,
  "created_at": "2026-01-20T10:00:00Z",
  "updated_at": "2026-01-23T14:00:00Z"
}
```

#### Create Store Indent

**Endpoint:** `POST /api/store/indents/`

**Permission:** Authenticated users (College Store Manager)

**Request:**
```json
{
  "college": 2,
  "requesting_store_manager": 10,
  "central_store": 1,
  "required_by_date": "2026-02-05",
  "priority": "high",
  "justification": "Required for new semester laboratory setup",
  "remarks": "Urgent requirement",
  "items": [
    {
      "central_store_item": 15,
      "requested_quantity": 50,
      "unit": "ream",
      "justification": "Lab consumables"
    },
    {
      "central_store_item": 20,
      "requested_quantity": 100,
      "unit": "piece",
      "justification": "Student requirements"
    }
  ]
}
```

**Response:** `201 Created`

**Validation:**
- Justification required for `urgent` priority
- Cannot approve quantity > requested quantity
- Central store must have sufficient stock for each item

#### Submit Indent

**Endpoint:** `POST /api/store/indents/{id}/submit/`

**Permission:** Authenticated users

**Response:**
```json
{
  "status": "pending_college_approval",
  "message": "Submitted to college admin for approval"
}
```

**Status Transition:** `draft` → `pending_college_approval`

#### College Admin Approve

**Endpoint:** `POST /api/store/indents/{id}/college_admin_approve/`

**Permission:** CanApproveIndent (College Admin)

**Response:**
```json
{
  "status": "pending_super_admin",
  "message": "Forwarded to super admin for approval"
}
```

**Validation:**
- Current status must be `pending_college_approval`
- User must be college admin for the indent's college

**Status Transition:** `pending_college_approval` → `pending_super_admin`

#### College Admin Reject

**Endpoint:** `POST /api/store/indents/{id}/college_admin_reject/`

**Permission:** CanApproveIndent

**Request:**
```json
{
  "reason": "Budget constraints for this quarter"
}
```

**Response:**
```json
{
  "status": "rejected_by_college",
  "message": "Rejected by college admin"
}
```

**Validation:**
- Current status must be `pending_college_approval`

**Status Transition:** `pending_college_approval` → `rejected_by_college`

#### Super Admin Approve

**Endpoint:** `POST /api/store/indents/{id}/super_admin_approve/`

**Permission:** IsCentralStoreManager (Super Admin)

**Response:**
```json
{
  "status": "super_admin_approved",
  "message": "Approved by super admin, forwarded to central store"
}
```

**Validation:**
- Current status must be `pending_super_admin`

**Status Transition:** `pending_super_admin` → `super_admin_approved`

**Side Effects:**
- Sets `approved_by` → current user
- Sets `approved_date` → current timestamp

#### Super Admin Reject

**Endpoint:** `POST /api/store/indents/{id}/super_admin_reject/`

**Permission:** IsCentralStoreManager

**Request:**
```json
{
  "reason": "Central store stock insufficient"
}
```

**Response:**
```json
{
  "status": "rejected_by_super_admin",
  "message": "Rejected by super admin"
}
```

**Validation:**
- Current status must be `pending_super_admin`

**Status Transition:** `pending_super_admin` → `rejected_by_super_admin`

#### Get Pending College Approvals

**Endpoint:** `GET /api/store/indents/pending_college_approvals/`

**Permission:** Authenticated users

**Description:** Returns indents pending college admin approval for the current user's college.

**Response:**
```json
[
  {
    "id": 5,
    "indent_number": "IND-2026-0005",
    "college": 2,
    "college_name": "Engineering College Mumbai",
    "status": "pending_college_approval",
    "priority": "medium",
    "indent_date": "2026-01-25"
  }
]
```

#### Get Pending Super Admin Approvals

**Endpoint:** `GET /api/store/indents/pending_super_admin_approvals/`

**Permission:** IsCentralStoreManager

**Description:** Returns all indents pending super admin approval.

**Response:**
```json
[
  {
    "id": 3,
    "indent_number": "IND-2026-0003",
    "college": 3,
    "college_name": "Medical College Pune",
    "status": "pending_super_admin",
    "priority": "high",
    "indent_date": "2026-01-23"
  }
]
```

#### Issue Materials

**Endpoint:** `POST /api/store/indents/{id}/issue_materials/`

**Permission:** IsCentralStoreManager

**Description:** Create a Material Issue Note for the approved indent.

**Request:**
```json
{
  "issue_date": "2026-01-24",
  "issued_by": 5,
  "transport_mode": "Truck",
  "vehicle_number": "MH-12-CD-5678",
  "driver_name": "Suresh Patil",
  "driver_contact": "+91-9876543210",
  "internal_notes": "Handle with care",
  "items": [
    {
      "indent_item": 1,
      "item": 15,
      "issued_quantity": 50,
      "unit": "ream",
      "batch_number": "BATCH-2026-01",
      "remarks": "Good condition"
    }
  ]
}
```

**Validation:**
- Indent status must be `super_admin_approved` or `approved`

**Response:** `200 OK` - Returns created MaterialIssueNote

---

### 2. Material Issue Note (MIN)

**Purpose:** Record and track material transfers from central store to colleges.

#### List Material Issue Notes

**Endpoint:** `GET /api/store/material-issues/`

**Query Parameters:**
- `status` - Filter by status: `prepared`, `dispatched`, `in_transit`, `received`, `cancelled`
- `receiving_college` - Filter by receiving college ID
- `issue_date` - Filter by issue date
- `search` - Search by min_number

**Response:**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "min_number": "MIN-2026-0001",
      "indent": 1,
      "status": "received",
      "issue_date": "2026-01-24"
    }
  ]
}
```

#### Get Material Issue Note Detail

**Endpoint:** `GET /api/store/material-issues/{id}/`

**Response:**
```json
{
  "id": 1,
  "min_number": "MIN-2026-0001",
  "indent": 1,
  "central_store": 1,
  "receiving_college": 2,
  "issue_date": "2026-01-24",
  "issued_by": 5,
  "received_by": 10,
  "transport_mode": "Truck",
  "vehicle_number": "MH-12-CD-5678",
  "driver_name": "Suresh Patil",
  "driver_contact": "+91-9876543210",
  "status": "received",
  "dispatch_date": "2026-01-24T10:00:00Z",
  "receipt_date": "2026-01-25T14:30:00Z",
  "min_document": "https://s3.amazonaws.com/bucket/material_issue_notes/MIN-2026-0001.pdf",
  "internal_notes": "Handle with care",
  "receipt_confirmation_notes": "All items received in good condition",
  "items": [
    {
      "id": 1,
      "material_issue": 1,
      "indent_item": 1,
      "item": 15,
      "issued_quantity": 50,
      "unit": "ream",
      "batch_number": "BATCH-2026-01",
      "remarks": "Good condition",
      "created_at": "2026-01-24T10:00:00Z",
      "updated_at": "2026-01-24T10:00:00Z"
    }
  ],
  "created_at": "2026-01-24T10:00:00Z",
  "updated_at": "2026-01-25T14:30:00Z"
}
```

#### Create Material Issue Note

**Endpoint:** `POST /api/store/material-issues/`

**Permission:** IsCentralStoreManager

**Request:**
```json
{
  "indent": 1,
  "central_store": 1,
  "receiving_college": 2,
  "issue_date": "2026-01-24",
  "issued_by": 5,
  "transport_mode": "Truck",
  "vehicle_number": "MH-12-CD-5678",
  "driver_name": "Suresh Patil",
  "driver_contact": "+91-9876543210",
  "internal_notes": "Handle with care",
  "items": [
    {
      "indent_item": 1,
      "item": 15,
      "issued_quantity": 50,
      "unit": "ream",
      "batch_number": "BATCH-2026-01",
      "remarks": "Good condition"
    }
  ]
}
```

**Response:** `201 Created`

**Validation:**
- Cannot issue quantity > approved quantity in indent item

#### Generate MIN PDF

**Endpoint:** `POST /api/store/material-issues/{id}/generate_pdf/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "pdf_generated"
}
```

#### Mark as Dispatched

**Endpoint:** `POST /api/store/material-issues/{id}/mark_dispatched/`

**Permission:** IsCentralStoreManager

**Response:**
```json
{
  "status": "dispatched"
}
```

**Side Effects (Signal-based when status = dispatched):**
1. Reduce central store inventory by issued quantities
2. Create InventoryTransaction (type: `issue`) for each item
3. Update IndentItem `issued_quantity`
4. Set `dispatch_date` → current timestamp

#### Confirm Receipt

**Endpoint:** `POST /api/store/material-issues/{id}/confirm_receipt/`

**Permission:** CanReceiveMaterials (College Store Manager)

**Request:**
```json
{
  "notes": "All items received in good condition"
}
```

**Response:**
```json
{
  "status": "received"
}
```

**Side Effects (Signal-based when status = received):**
1. Find or create college store item (same code as central item)
2. Create StockReceive for college
3. Update college item stock quantity
4. Check indent fulfillment status
5. Set `receipt_date` → current timestamp
6. Set `received_by` → current user
7. Set `receipt_confirmation_notes` → provided notes

---

## Status Flow Diagrams

### Procurement Requirement Flow

```
draft → submitted → pending_approval → approved → quotations_received → po_created → fulfilled
                                    ↓
                                cancelled
```

### Purchase Order Flow

```
draft → sent → acknowledged → partially_received → fulfilled
        ↓
    cancelled
```

### Goods Receipt Note Flow

```
received → pending_inspection → inspected → approved → posted_to_inventory
           ↓
        rejected
```

### Store Indent Flow (Two-Level Approval)

```
draft → submitted → pending_college_approval → pending_super_admin → super_admin_approved → partially_fulfilled → fulfilled
                           ↓                            ↓
                    rejected_by_college        rejected_by_super_admin
```

**Legacy Flow (for backward compatibility):**
```
draft → submitted → pending_approval → approved → partially_fulfilled → fulfilled
                           ↓
                        rejected
```

### Material Issue Note Flow

```
prepared → dispatched → in_transit → received
           ↓
       cancelled
```

---

## Permissions

### Permission Classes

1. **IsCentralStoreManager**
   - Required: Super Admin (`is_superuser=True`)
   - Used for: All central store operations

2. **IsCentralStoreManagerOrReadOnly**
   - Read: Anyone authenticated
   - Write: Super Admin only
   - Used for: Supplier, Central Store viewsets

3. **IsCollegeStoreManager**
   - Required: Authenticated user with `college_id`
   - Used for: College store operations

4. **IsCEOOrFinance**
   - Required: Super Admin OR member of CEO/Finance group
   - Used for: Quotation selection

5. **CanApproveIndent**
   - Required: Super Admin OR College Admin with `college_id`
   - Used for: Indent approvals

6. **CanReceiveMaterials**
   - Required: Authenticated user with `college_id`
   - Used for: Confirming material receipt

### User Types

- `super_admin` - Full access to all modules
- `college_admin` - Can approve indents for their college
- `staff` - Can approve indents for their college
- College Store Manager - User with `college_id` (can create indents, receive materials)

---

## Dependencies

### Module Dependencies

**Procurement depends on:**
- `apps.core` - College, CollegeScopedModel, AuditModel
- `apps.approvals` - ApprovalRequest for requirement approvals
- `apps.accounts` - User model for managers and approvers

**Transfers depends on:**
- `apps.core` - College, CollegeScopedModel
- Procurement module - CentralStore, CentralStoreInventory, StoreItem

### Database Relationships

**Procurement:**
```
ProcurementRequirement (1) → (N) RequirementItem
ProcurementRequirement (1) → (N) SupplierQuotation
SupplierQuotation (1) → (N) QuotationItem
SupplierQuotation (1) → (N) PurchaseOrder
PurchaseOrder (1) → (N) PurchaseOrderItem
PurchaseOrder (1) → (N) GoodsReceiptNote
GoodsReceiptNote (1) → (N) GoodsReceiptItem
GoodsReceiptNote (1) → (1) InspectionNote
```

**Transfers:**
```
StoreIndent (1) → (N) IndentItem
StoreIndent (1) → (N) MaterialIssueNote
MaterialIssueNote (1) → (N) MaterialIssueItem
```

**Inventory:**
```
CentralStore (1) → (N) CentralStoreInventory
CentralStoreInventory (1) → (N) InventoryTransaction
```

### Signal-Based Workflows

**On GoodsReceiptNote status = posted_to_inventory:**
- Update PurchaseOrderItem.received_quantity
- Update/Create CentralStoreInventory
- Create InventoryTransaction (receipt)
- Create StockReceive
- Check PO fulfillment

**On MaterialIssueNote status = dispatched:**
- Reduce CentralStoreInventory
- Create InventoryTransaction (issue)
- Update IndentItem.issued_quantity

**On MaterialIssueNote status = received:**
- Create/Update college StoreItem
- Create StockReceive for college
- Update college item stock
- Check Indent fulfillment

**On ProcurementRequirement status = submitted:**
- Create ApprovalRequest
- Set approvers
- Change status to pending_approval

---

## Best Practices for Frontend Integration

### 1. Token Management

```javascript
// Store token after login
const login = async (username, password) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  localStorage.setItem('authToken', data.key);
  localStorage.setItem('user', JSON.stringify(data.user));
};

// Use token in requests
const fetchWithAuth = (url, options = {}) => {
  const token = localStorage.getItem('authToken');
  return fetch(url, {
    ...options,
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });
};
```

### 2. Error Handling

```javascript
const handleApiError = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    } else if (response.status === 403) {
      // Permission denied
      alert('You do not have permission to perform this action');
    } else if (response.status === 400) {
      // Validation error
      console.error('Validation errors:', error);
      return error;
    }
    throw new Error(error.detail || 'An error occurred');
  }
  return response.json();
};
```

### 3. Pagination

```javascript
const fetchAllPages = async (url) => {
  let results = [];
  let nextUrl = url;

  while (nextUrl) {
    const response = await fetchWithAuth(nextUrl);
    const data = await response.json();
    results = [...results, ...data.results];
    nextUrl = data.next;
  }

  return results;
};
```

### 4. File Upload

```javascript
const uploadFile = async (url, file, additionalData = {}) => {
  const formData = new FormData();
  formData.append('file', file);

  Object.keys(additionalData).forEach(key => {
    formData.append(key, additionalData[key]);
  });

  const token = localStorage.getItem('authToken');
  return fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`
      // Don't set Content-Type for FormData
    },
    body: formData
  });
};
```

### 5. Status-Based UI

```javascript
const getStatusBadgeColor = (status) => {
  const statusColors = {
    'draft': 'gray',
    'submitted': 'blue',
    'pending_approval': 'yellow',
    'pending_college_approval': 'yellow',
    'pending_super_admin': 'orange',
    'approved': 'green',
    'super_admin_approved': 'green',
    'fulfilled': 'green',
    'rejected': 'red',
    'rejected_by_college': 'red',
    'rejected_by_super_admin': 'red',
    'cancelled': 'gray'
  };
  return statusColors[status] || 'gray';
};
```

### 6. Nested Object Creation

```javascript
// Create Procurement Requirement with items
const createRequirement = async (requirementData) => {
  const response = await fetchWithAuth('/api/store/procurement/requirements/', {
    method: 'POST',
    body: JSON.stringify({
      central_store: 1,
      title: requirementData.title,
      required_by_date: requirementData.requiredByDate,
      urgency: requirementData.urgency,
      justification: requirementData.justification,
      items: requirementData.items.map(item => ({
        item_description: item.description,
        category: item.categoryId,
        quantity: item.quantity,
        unit: item.unit,
        estimated_unit_price: item.estimatedPrice,
        specifications: item.specifications
      }))
    })
  });

  return handleApiError(response);
};
```

---

## Example API Calls

### Complete Procurement Flow

```javascript
// 1. Create Requirement
const requirement = await createRequirement({
  central_store: 1,
  title: "Q1 Office Supplies",
  required_by_date: "2026-02-01",
  urgency: "medium",
  justification: "Quarterly requirement",
  items: [
    {
      item_description: "A4 Paper",
      category: 2,
      quantity: 100,
      unit: "ream",
      estimated_unit_price: "250.00"
    }
  ]
});

// 2. Submit for approval
await fetchWithAuth(
  `/api/store/procurement/requirements/${requirement.id}/submit_for_approval/`,
  { method: 'POST' }
);

// 3. Get quotations (after suppliers submit)
const quotations = await fetchWithAuth(
  `/api/store/procurement/requirements/${requirement.id}/quotations/`
);

// 4. Compare quotations
const comparison = await fetchWithAuth(
  `/api/store/procurement/requirements/${requirement.id}/compare_quotations/`
);

// 5. Select best quotation
await fetchWithAuth(
  `/api/store/procurement/requirements/${requirement.id}/select_quotation/`,
  {
    method: 'POST',
    body: JSON.stringify({ quotation_id: quotations[0].id })
  }
);

// 6. Create Purchase Order
const po = await createPurchaseOrder({
  requirement: requirement.id,
  quotation: quotations[0].id,
  supplier: quotations[0].supplier,
  // ... other PO details
});

// 7. Send to Supplier
await fetchWithAuth(
  `/api/store/procurement/purchase-orders/${po.id}/send_to_supplier/`,
  { method: 'POST' }
);

// 8. Create GRN (when goods arrive)
const grn = await createGRN({
  purchase_order: po.id,
  // ... GRN details
});

// 9. Post to Inventory
await fetchWithAuth(
  `/api/store/procurement/goods-receipts/${grn.id}/post_to_inventory/`,
  { method: 'POST' }
);
```

### Complete Transfer Flow

```javascript
// 1. Create Indent
const indent = await createIndent({
  college: 2,
  central_store: 1,
  required_by_date: "2026-02-05",
  priority: "high",
  justification: "Lab setup",
  items: [
    {
      central_store_item: 15,
      requested_quantity: 50,
      unit: "ream"
    }
  ]
});

// 2. Submit
await fetchWithAuth(
  `/api/store/indents/${indent.id}/submit/`,
  { method: 'POST' }
);

// 3. College Admin Approve
await fetchWithAuth(
  `/api/store/indents/${indent.id}/college_admin_approve/`,
  { method: 'POST' }
);

// 4. Super Admin Approve
await fetchWithAuth(
  `/api/store/indents/${indent.id}/super_admin_approve/`,
  { method: 'POST' }
);

// 5. Issue Materials
const min = await fetchWithAuth(
  `/api/store/indents/${indent.id}/issue_materials/`,
  {
    method: 'POST',
    body: JSON.stringify({
      issue_date: "2026-01-24",
      transport_mode: "Truck",
      // ... other MIN details
    })
  }
);

// 6. Mark Dispatched
await fetchWithAuth(
  `/api/store/material-issues/${min.id}/mark_dispatched/`,
  { method: 'POST' }
);

// 7. Confirm Receipt (college side)
await fetchWithAuth(
  `/api/store/material-issues/${min.id}/confirm_receipt/`,
  {
    method: 'POST',
    body: JSON.stringify({
      notes: "All items received in good condition"
    })
  }
);
```

---

## Support & Troubleshooting

### Common Issues

**Issue: 401 Unauthorized**
- Ensure token is included in Authorization header
- Check if token has expired (re-login)
- Verify token format: `Token your_token_here`

**Issue: 403 Forbidden**
- User doesn't have required permissions
- Check user type (super_admin, college_admin, etc.)
- Verify user's college_id matches resource scope

**Issue: 400 Validation Error**
- Check required fields are provided
- Verify field formats (dates, decimals, integers)
- Review nested object structures (items arrays)
- Check field constraints (quantity > 0, etc.)

**Issue: Status transition not allowed**
- Verify current status allows the action
- Check approval workflow requirements
- Ensure prerequisite steps are completed

### Debug Tips

1. **Check Response Headers**
   ```javascript
   response.headers.forEach((value, key) => {
     console.log(key, value);
   });
   ```

2. **Log Full Error Response**
   ```javascript
   const error = await response.json();
   console.error('Full error:', JSON.stringify(error, null, 2));
   ```

3. **Verify Payload Structure**
   ```javascript
   console.log('Sending:', JSON.stringify(payload, null, 2));
   ```

---

**End of Documentation**

For additional support or clarification, please contact the backend development team.
