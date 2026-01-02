# Central Store Enhancements

## Overview
- Added central store procurement-to-distribution workflow with supplier master, central inventory, procurement, GRN, indent, and material issue tracking.
- Integrated approval hooks for procurement requirements, goods inspections, and store indents.
- Added PDF stubs for PO/MIN/GRN and document numbering utility for all workflow documents.

## Key Models
- SupplierMaster, CentralStore
- ProcurementRequirement, RequirementItem, SupplierQuotation, QuotationItem
- PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GoodsReceiptItem, InspectionNote
- StoreIndent, IndentItem, MaterialIssueNote, MaterialIssueItem
- CentralStoreInventory, InventoryTransaction
- StoreItem updated with `managed_by` and optional `central_store` link.

## Permissions
- IsCentralStoreManager(OrReadOnly), IsCollegeStoreManager, IsCEOOrFinance, CanApproveIndent, CanReceiveMaterials.

## Utilities
- `generate_document_number(prefix, model_class, field_name)` for PREFIX-YYYY-NNNNN sequencing.
- PDF helpers: `generate_po_pdf`, `generate_min_pdf`, `generate_grn_pdf` (WeasyPrint if available).

## API Endpoints (base: `/api/store/`)
- `GET/POST/PUT/DELETE suppliers/` — Supplier master; `POST suppliers/{id}/verify/`
- `GET/POST/PUT/DELETE central-stores/` — Central store; `GET central-stores/{id}/inventory/`, `GET central-stores/{id}/stock-summary/`
- `GET/POST/PUT/DELETE procurement/requirements/` — Requirement CRUD; `POST {id}/submit-for-approval/`, `GET {id}/quotations/`, `POST {id}/select-quotation/`
- `GET/POST/PUT/DELETE procurement/quotations/` — Quotation CRUD (supports inline supplier via `create_new_supplier`); `POST {id}/mark-selected/`
- `GET/POST/PUT/DELETE procurement/purchase-orders/` — PO CRUD; `POST {id}/generate-pdf/`, `POST {id}/send-to-supplier/`, `POST {id}/acknowledge/`
- `GET/POST/PUT/DELETE procurement/goods-receipts/` — GRN CRUD; `POST {id}/submit-for-inspection/`, `POST {id}/post-to-inventory/`
- `GET/POST/PUT/DELETE procurement/inspections/` — Inspection notes
- `GET/POST/PUT/DELETE indents/` — Store indent CRUD; `POST {id}/submit/`, `POST {id}/approve/`, `POST {id}/reject/`
- `GET/POST/PUT/DELETE material-issues/` — Material issue note CRUD; `POST {id}/generate-pdf/`, `POST {id}/dispatch/`, `POST {id}/confirm-receipt/`
- `GET/POST/PUT/DELETE central-inventory/` — Central inventory; `GET central-inventory/low-stock/`, `POST central-inventory/{id}/adjust-stock/`
- `GET inventory-transactions/` — Transaction history
- Existing store endpoints retained: categories/, items/, vendors/, stock-receipts/, sales/, sale-items/, print-jobs/, credits/

## Notes
- ApprovalRequest types expanded for procurement_requirement, goods_inspection, store_indent; approval signal updates linked records on approve/reject.
- Signals handle basic stock adjustments, quotation selection exclusivity, PO status update, and indent approval hooks.
- PDF templates live in `apps/store/templates/store/pdf/` (placeholders).
