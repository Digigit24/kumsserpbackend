# KUMSS ERP - Accounting Module Documentation

**Module:** `apps.accounting`  
**Version:** 1.0.0  
**Status:** Official Technical Reference  
**Last Updated:** 2026-01-01

---

## 1. Executive Summary

The **Accounting Module** is a robust double-entry bookkeeping system designed to track institutional finances. It manages revenue (Income), operational costs (Expenses), banking infrastructure (Accounts), and fiscal tracking (Financial Years).

Like other modules in KUMSS ERP, it is strictly **Multi-Tenant**, ensuring that each college's financial ledger remains isolated and secure.

---

## 2. Structural Overview

The app is built around the core concept of **Tracking Money Flow**.

- **Categorization**: All funds are classified into Income or Expense categories.
- **Banking**: Physical/Virtual bank accounts are managed to track real balances.
- **Auditability**: Every movement of money generates an `AccountTransaction` record, ensuring a perfect audit trail.

---

## 3. Database Models Reference

### 3.1 Setup & Configuration

- **`IncomeCategory`**: Grouping for revenue sources (e.g., Fees, Donations, Grants).
- **`ExpenseCategory`**: Grouping for costs (e.g., Salary, Electricity, Maintenance).
- **`FinancialYear`**: Maps the fiscal period (e.g., April to March) and identifies which year is "Current."

### 3.2 Banking & Transactions

- **`Account`**: Represents a bank account or cash-in-hand. Stores real-time `balance`.
- **`AccountTransaction`**: **The Master Ledger.** Every time money moves, a record is created here with `balance_after`. It links to an `Account`.

### 3.3 Operations

- **`Income`**: Records specific revenue entries. Includes `invoice_number` and optional digital `invoice_file`.
- **`Expense`**: Records specific cost entries. Includes `receipt_number`, `paid_to`, and optional digital `receipt_file`.
- **`Voucher`**: Official paper-trail entities for auditing purposes.

---

## 4. Logical Flow (Money Lifecycle)

1.  **Preparation**: College admin defines `IncomeCategory` and `ExpenseCategory`.
2.  **Infrastructure**: Bank accounts are registered in the `Account` model.
3.  **Revenue Generation**:
    - Income is recorded in the `Income` model.
    - _System Logic:_ This should trigger an update to the linked `Account` balance and create an `AccountTransaction`.
4.  **Operational Spending**:
    - Expenses are recorded in the `Expense` model.
    - _System Logic:_ This deducts from the `Account` balance and logs a transaction record.

---

## 5. API Reference

### 5.1 Key Endpoints

| Resource       | Endpoint                                | Description                             |
| :------------- | :-------------------------------------- | :-------------------------------------- |
| **Accounts**   | `/api/accounting/accounts/`             | Manage bank accounts and view balances. |
| **Revenue**    | `/api/accounting/income/`               | Log new income and upload invoices.     |
| **Spending**   | `/api/accounting/expenses/`             | Log new expenses and upload receipts.   |
| **History**    | `/api/accounting/account-transactions/` | View the full financial audit trail.    |
| **Categories** | `/api/accounting/income-categories/`    | Manage revenue categories.              |

### 5.2 Filtering Capabilities

The APIs allow deep-dive analysis via query parameters:

- `?category=<id>`: Filter finances by type.
- `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`: Date range reporting.
- `?account=<id>`: See transactions for a specific bank account.

---

## 6. Technical Implementation Details

### 6.1 Multi-Tenancy Scoping

All models (except the low-level `AccountTransaction` which links to `Account`) inherit from `CollegeScopedModel`. Multi-tenancy is enforced at the DB query layer via the `X-College-ID` header.

### 6.2 Transactional Integrity

The accounting logic relies heavily on **Django Signals** (specifically `post_save`). When an Income or Expense is created:

1.  The `Account` balance is updated.
2.  The `AccountTransaction` is automatically generated.
    This ensures the ledger never goes "out of sync" even if an entry is made via the admin panel.

### 6.3 Security

- **Soft Deletion**: Records use `is_active` to prevent accidental loss of financial history.
- **Audit Fields**: Every record tracks who created/updated it and when.

---

_End of Documentation_
