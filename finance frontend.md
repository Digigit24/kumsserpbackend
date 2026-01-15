# Finance Module - Frontend API Documentation

## Overview
Central finance module aggregating all money-related transactions from existing apps.

---

## Finance App Structure

### Core Tables
1. **AppExpense** - Expense tracking per app
2. **AppIncome** - Income tracking per app
3. **AppTotal** - Net total per app (income - expense)
4. **FinanceTotal** - Overall totals
5. **OtherExpense** - Additional expenses

---

## Existing Money-Related APIs

### 1. FEES APP (Primary Income Source)

#### Income Endpoints
| Endpoint | Method | Purpose | Amount Field |
|----------|--------|---------|--------------|
| `/api/v1/fees/fee-collections/` | POST | Collect fee payment | `amount` |
| `/api/v1/fees/fee-fines/` | POST | Apply late fine | `amount` |
| `/api/v1/fees/bank-payments/` | POST | Bank payment | via fee collection |
| `/api/v1/fees/online-payments/` | POST | Online payment | via fee collection |

#### Expense Endpoints
| Endpoint | Method | Purpose | Amount Field |
|----------|--------|---------|--------------|
| `/api/v1/fees/fee-refunds/` | POST | Process refund | `amount` |

---

### 2. LIBRARY APP (Income)

#### Income Endpoints
| Endpoint | Method | Purpose | Amount Field |
|----------|--------|---------|--------------|
| `/api/v1/library/fines/` | POST | Library fine | `amount` |
| `/api/v1/library/returns/` | POST | Return fine/damage | `fine_amount`, `damage_charges` |

---

### 3. HOSTEL APP (Income)

#### Income Endpoints
| Endpoint | Method | Purpose | Amount Field |
|----------|--------|---------|--------------|
| `/api/v1/hostel/fees/` | POST | Hostel fee collection | `amount` |

---

### 4. HR APP (Expense)

#### Expense Endpoints
| Endpoint | Method | Purpose | Amount Field |
|----------|--------|---------|--------------|
| `/api/v1/hr/payrolls/` | POST | Process payroll | `net_salary` |
| `/api/v1/hr/salary-structures/` | GET/POST | Salary setup | `gross_salary` |

---

### 5. STORE APP (Mixed)

#### Income Endpoints
| Endpoint | Method | Purpose | Amount Field |
|----------|--------|---------|--------------|
| `/api/v1/store/sales/` | POST | Store sale | `total_amount` |
| `/api/v1/store/print-jobs/` | POST | Print job | `total_amount` |

#### Expense Endpoints
| Endpoint | Method | Purpose | Amount Field |
|----------|--------|---------|--------------|
| `/api/v1/store/stock-receipts/` | POST | Stock purchase | `total_amount` |
| `/api/v1/store/procurement/purchase-orders/` | POST | Purchase order | `grand_total` |
| `/api/v1/store/procurement/goods-receipts/` | POST | Goods receipt | `invoice_amount` |

---

## New Finance APIs (To Be Created)

### Base URL: `/api/v1/finance/`

### 1. Other Expenses
```
POST   /api/v1/finance/other-expenses/
GET    /api/v1/finance/other-expenses/
GET    /api/v1/finance/other-expenses/{id}/
PUT    /api/v1/finance/other-expenses/{id}/
DELETE /api/v1/finance/other-expenses/{id}/

Request Body:
{
  "title": "string",
  "description": "string",
  "amount": decimal,
  "category": "string",
  "date": "date",
  "receipt": "file (optional)"
}
```

### 2. App-wise Summary
```
GET /api/v1/finance/app-summary/

Response:
{
  "fees": {
    "income": 1500000,
    "expense": 50000,
    "total": 1450000
  },
  "library": {
    "income": 25000,
    "expense": 0,
    "total": 25000
  },
  "hostel": {
    "income": 800000,
    "expense": 0,
    "total": 800000
  },
  "hr": {
    "income": 0,
    "expense": 2000000,
    "total": -2000000
  },
  "store": {
    "income": 150000,
    "expense": 500000,
    "total": -350000
  },
  "other": {
    "income": 0,
    "expense": 100000,
    "total": -100000
  }
}
```

### 3. Overall Totals
```
GET /api/v1/finance/totals/

Response:
{
  "total_income": 2475000,
  "total_expense": 2650000,
  "net_total": -175000,
  "last_updated": "2026-01-15T10:30:00Z"
}
```

### 4. Transaction History
```
GET /api/v1/finance/transactions/
Query Params: ?app=fees&type=income&from_date=2026-01-01&to_date=2026-01-31

Response:
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "app": "fees",
      "type": "income",
      "amount": 5000,
      "description": "Fee collection",
      "reference_id": 123,
      "date": "2026-01-15",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

### 5. Monthly Report
```
GET /api/v1/finance/reports/monthly/
Query Params: ?year=2026&month=1

Response:
{
  "month": "2026-01",
  "apps": {
    "fees": {"income": 150000, "expense": 5000},
    "library": {"income": 2500, "expense": 0},
    "hostel": {"income": 80000, "expense": 0},
    "hr": {"income": 0, "expense": 200000},
    "store": {"income": 15000, "expense": 50000},
    "other": {"income": 0, "expense": 10000}
  },
  "total_income": 247500,
  "total_expense": 265000,
  "net": -17500
}
```

### 6. Dashboard Stats
```
GET /api/v1/finance/dashboard/

Response:
{
  "current_month": {
    "income": 247500,
    "expense": 265000,
    "net": -17500
  },
  "previous_month": {
    "income": 230000,
    "expense": 250000,
    "net": -20000
  },
  "current_year": {
    "income": 2475000,
    "expense": 2650000,
    "net": -175000
  },
  "top_income_sources": [
    {"app": "fees", "amount": 1500000},
    {"app": "hostel", "amount": 800000}
  ],
  "top_expense_sources": [
    {"app": "hr", "amount": 2000000},
    {"app": "store", "amount": 500000}
  ]
}
```

---

## Frontend Flow

### 1. Dashboard Page
- Fetch `/api/v1/finance/dashboard/`
- Display cards: Total Income, Total Expense, Net Balance
- Show charts: Monthly trends, App-wise breakdown
- Top income/expense sources

### 2. App-wise Summary Page
- Fetch `/api/v1/finance/app-summary/`
- Display table with all apps
- Columns: App Name, Income, Expense, Total
- Click app → View detailed transactions

### 3. Transaction History Page
- Fetch `/api/v1/finance/transactions/`
- Filters: App, Type (income/expense), Date range
- Display paginated table
- Export to CSV/PDF

### 4. Other Expenses Page
- Fetch `/api/v1/finance/other-expenses/`
- Create new expense form
- Upload receipt
- List all other expenses
- Edit/Delete functionality

### 5. Reports Page
- Monthly/Yearly reports
- Fetch `/api/v1/finance/reports/monthly/`
- Date range selector
- Downloadable reports
- Charts and graphs

---

## Data Sync Strategy

### Background Jobs (Django Celery)
1. **Periodic Sync** - Every hour
   - Query all money transactions from fees/library/hostel/hr/store
   - Update AppIncome/AppExpense tables
   - Recalculate AppTotal and FinanceTotal

2. **Real-time Hooks** - On transaction create/update
   - Use Django signals (post_save, post_delete)
   - Auto-update finance tables when:
     - FeeCollection created → Update fees income
     - FeeRefund created → Update fees expense
     - Payroll created → Update hr expense
     - StoreSale created → Update store income
     - PurchaseOrder created → Update store expense
     - LibraryFine created → Update library income
     - HostelFee created → Update hostel income

---

## Database Schema (Finance App)

### Models

```python
# App-wise Income
class AppIncome(models.Model):
    app_name = CharField  # fees, library, hostel, store
    month = DateField
    amount = DecimalField
    transaction_count = IntegerField

# App-wise Expense
class AppExpense(models.Model):
    app_name = CharField  # fees, hr, store, other
    month = DateField
    amount = DecimalField
    transaction_count = IntegerField

# App-wise Total
class AppTotal(models.Model):
    app_name = CharField
    month = DateField
    income = DecimalField
    expense = DecimalField
    net_total = DecimalField

# Overall Total
class FinanceTotal(models.Model):
    month = DateField
    total_income = DecimalField
    total_expense = DecimalField
    net_total = DecimalField

# Other Expenses
class OtherExpense(models.Model):
    title = CharField
    description = TextField
    amount = DecimalField
    category = CharField
    date = DateField
    receipt = FileField
    created_by = ForeignKey(User)
    created_at = DateTimeField
```

---

## Implementation Checklist

- [ ] Create finance app
- [ ] Define models
- [ ] Create serializers
- [ ] Implement viewsets
- [ ] Setup URL routing
- [ ] Create Django signals for auto-sync
- [ ] Setup Celery periodic task for hourly sync
- [ ] Create management command for initial data sync
- [ ] Add permissions (only admin access)
- [ ] Create API documentation
- [ ] Testing

---

## Permissions
- Only Super Admin and Finance Manager roles
- Read-only for College Admin
- No access for other users

---

## Notes
- All amounts in Decimal(10, 2)
- Currency: INR (₹)
- Date format: YYYY-MM-DD
- DateTime format: ISO 8601
- Pagination: 50 items per page
- All POST/PUT/DELETE require authentication token
