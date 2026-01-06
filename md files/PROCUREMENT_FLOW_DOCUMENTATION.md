# Procurement and Store Management Flow Documentation

This document provides a comprehensive overview of the Procurement and Store management processes within the ERP system. It is designed to help React developers understand the business logic, status transitions, and API interactions required for the Store module.

---

## 1. Key Terminology

| Term                          | Description                                                                                             |
| :---------------------------- | :------------------------------------------------------------------------------------------------------ |
| **Central Store**             | The primary warehouse that manages inventory for all colleges.                                          |
| **Store Item**                | A specific product or material tracked in the inventory.                                                |
| **Material Indent**           | An internal request from a college department/store to the Central Store for items.                     |
| **Procurement Requirement**   | A formal request created when items are not available or need to be purchased from external vendors.    |
| **Supplier/Vendor**           | External entities that provide goods or services.                                                       |
| **Quotation**                 | A formal price offer from a supplier for a specific Procurement Requirement.                            |
| **Purchase Order (PO)**       | A legal contract sent to a supplier to buy specific items at agreed prices.                             |
| **Goods Receipt Note (GRN)**  | A document used to record the delivery of goods from a supplier.                                        |
| **Inspection Note**           | A quality check report performed on received goods before they are added to inventory.                  |
| **Material Issue Note (MIN)** | A document issued by the Central Store when items are dispatched to a college in response to an indent. |

---

## 2. Core Procurement Flow (External Purchase)

This flow tracks the acquisition of goods from external vendors.

### Step 1: Procurement Requirement

- **Action**: Store Manager identifies a need and creates a `ProcurementRequirement`.
- **Status**: `draft` -> `submitted` -> `approved`.
- **Model**: `ProcurementRequirement`, `RequirementItem`.

### Step 2: Supplier Quotations

- **Action**: Request for Quotation (RFQ) is sent to vendors. Vendors submit `SupplierQuotation`.
- **Action**: Procurement team records these quotations in the system.
- **Frontend Note**: The `SupplierQuotationCreateSerializer` is configured to accept **only** file uploads (`quotation_file`). Ensure your upload component supports `.pdf`, `.jpg`, `.jpeg`, and `.png` (as per business requirements).
- **Model**: `SupplierQuotation`, `QuotationItem`.

### Step 3: Selection and PO Creation

- **Action**: A quotation is marked as "Selected".
- **Action**: A `PurchaseOrder` is generated from the selected quotation.
- **Status (PO)**: `draft` -> `sent` -> `acknowledged`.
- **Model**: `PurchaseOrder`, `PurchaseOrderItem`.

### Step 4: Goods Receipt (GRN)

- **Action**: Goods arrive at the warehouse. A `GoodsReceiptNote` is created.
- **Linking**: Linked to the `PurchaseOrder`.
- **Status**: `received` -> `pending_inspection`.
- **Model**: `GoodsReceiptNote`, `GoodsReceiptItem`.

### Step 5: Inspection

- **Action**: Quality team inspects the items and creates an `InspectionNote`.
- **Action**: Items are either accepted, partially accepted, or rejected.
- **Model**: `InspectionNote`.

### Step 6: Post to Inventory

- **Action**: Once inspected, the Store Manager clicks "Post to Inventory".
- **Effect**: The `CentralStoreInventory` is updated (quantities increase).
- **Status (GRN)**: `posted_to_inventory`.

---

## 3. Internal Indent Flow (Store to Store)

This flow handles requests for items from individual college stores to the Central Store.

### Step 1: Create Indent

- **Actor**: College Store Manager.
- **Action**: Creates a `StoreIndent` with multiple `IndentItem`s.
- **Status**: `draft`.

### Step 2: Submission and Multi-Level Approval

1.  **Submit**: Manager submits to College Admin (`status: submitted`).
2.  **College Admin Approve**: Approves and forwards to Super Admin (`status: college_admin_approved`).
3.  **Super Admin Approve**: Final approval (`status: super_admin_approved`).

- **Model**: `StoreIndent`.

### Step 3: Material Issue (MIN)

- **Actor**: Central Store Manager.
- **Action**: Once an indent is `super_admin_approved`, the manager issues items via `MaterialIssueNote`.
- **Effect**: Stock is deducted from `CentralStoreInventory`.
- **Status (MIN)**: `issued` -> `dispatched`.
- **Model**: `MaterialIssueNote`, `MaterialIssueItem`.

### Step 4: Acknowledgment

- **Actor**: Receiving College Store Manager.
- **Action**: Confirms receipt of materials.
- **Status (MIN)**: `received`.

---

## 4. Roles & Permissions

| Role                      | Primary Responsibilities                                                                          |
| :------------------------ | :------------------------------------------------------------------------------------------------ |
| **Super Admin**           | Final approval on Indents and Procurement Requirements.                                           |
| **College Admin**         | Intermediate approval for Indents from their specific college.                                    |
| **Central Store Manager** | Managing external procurement (PO, GRN), managing central inventory, and issuing materials (MIN). |
| **College Store Manager** | Creating indents, receiving materials, and managing local college stock.                          |

---

## 5. API Integration for React Developers

### Major ViewSets

- `/api/v1/store/requirements/`: Manage procurement needs.
- `/api/v1/store/quotations/`: Manage vendor quotes.
- `/api/v1/store/purchase-orders/`: PO management (includes PDF generation).
- `/api/v1/store/grn/`: Goods receipt and posting to inventory.
- `/api/v1/store/indents/`: Internal requests and approval actions.
- `/api/v1/store/material-issue/`: Issuing items from central store.

### Custom Actions (Frontend Buttons)

React developers should look for these custom `@action` endpoints on the ViewSets:

- **Requirements**: `submit_for_approval()`, `approve()`, `compare_quotations()` (for side-by-side view), `select_quotation()`.
- **PO**: `generate_pdf()` (Generates the PO PDF on the server), `send_to_supplier()`, `acknowledge()`.
- **GRN**: `submit_for_inspection()`, `post_to_inventory()`.
- **Indents**: `submit()`, `college_admin_approve()`, `super_admin_approve()`, `issue_materials()`.
- **Material Issue**: `generate_pdf()`, `mark_dispatched()`, `confirm_receipt()`.

### PDF Generation

Several modules support PDF generation. The API typically returns a success status, and the PDF is stored or served. Check the `generate_pdf` actions specifically.

---

## 6. Frontend Display Logic Recommendations

1.  **Status Badges**: Use color-coded badges for different statuses (e.g., Green for `Approved`/`Posted`, Yellow for `Pending`, Red for `Cancelled`).
2.  **Conditional Actions**: Only show "Approve" buttons if the current user has the correct role and the document is in the correct state.
3.  **Real-time Stock**: Before creating an Indent or MIN, fetch the current available quantity from `CentralStoreInventory` to prevent over-drawing.
4.  **Nested Forms**: Use dynamic row addition for `RequirementItem`, `QuotationItem`, and `IndentItem` during creation.

---

_Last Updated: January 6, 2026_
