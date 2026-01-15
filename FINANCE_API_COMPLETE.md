# Finance API - Complete Reference

Base URL: `/api/v1/finance/`

---

## 1. Other Expenses (Manual Entry)

### Create Expense
```
POST /api/v1/finance/other-expenses/
{
  "title": "Electricity Bill",
  "description": "January 2026",
  "amount": 15000.00,
  "category": "utilities",
  "payment_method": "bank",
  "date": "2026-01-15"
}
```

**Categories:** `maintenance`, `utilities`, `supplies`, `marketing`, `travel`, `miscellaneous`
**Payment Methods:** `cash`, `bank`, `online`, `cheque`, `upi`

### List/Get/Update/Delete
```
GET    /api/v1/finance/other-expenses/
GET    /api/v1/finance/other-expenses/{id}/
PUT    /api/v1/finance/other-expenses/{id}/
DELETE /api/v1/finance/other-expenses/{id}/
```

---

## 2. App Summary
```
GET /api/v1/finance/reports/app_summary/

Response:
{
  "fees": {"income": 1500000, "expense": 50000, "total": 1450000},
  "library": {"income": 25000, "expense": 0, "total": 25000},
  "hostel": {"income": 800000, "expense": 0, "total": 800000},
  "hr": {"income": 0, "expense": 2000000, "total": -2000000},
  "store": {"income": 150000, "expense": 500000, "total": -350000},
  "other": {"income": 0, "expense": 100000, "total": -100000}
}
```

---

## 3. Overall Totals
```
GET /api/v1/finance/reports/totals/

Response:
{
  "total_income": 2475000,
  "total_expense": 2650000,
  "net_total": -175000,
  "last_updated": "2026-01-15T10:30:00Z"
}
```

---

## 4. Monthly Report
```
GET /api/v1/finance/reports/monthly/?year=2026&month=1

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

---

## 5. Dashboard Stats
```
GET /api/v1/finance/reports/dashboard/

Response:
{
  "current_month": {"income": 247500, "expense": 265000, "net": -17500},
  "previous_month": {"income": 230000, "expense": 250000, "net": -20000},
  "current_year": {"income": 2475000, "expense": 2650000, "net": -175000},
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

## 6. Financial Projections ⭐ NEW
```
GET /api/v1/finance/reports/projections/

Response:
{
  "based_on_months": 3,
  "monthly_average": {
    "income": 825000,
    "expense": 883333,
    "net": -58333
  },
  "projections": {
    "1_year": {
      "income": {"min": 7920000, "avg": 9900000, "max": 11880000},
      "expense": {"min": 8479996, "avg": 10599996, "max": 12719996},
      "net": {"min": -559996, "avg": -699996, "max": -839996}
    },
    "3_year": {
      "income": {"min": 23760000, "avg": 29700000, "max": 35640000},
      "expense": {"min": 25439988, "avg": 31799988, "max": 38159988},
      "net": {"min": -1679988, "avg": -2099988, "max": -2519988}
    },
    "5_year": {
      "income": {"min": 39600000, "avg": 49500000, "max": 59400000},
      "expense": {"min": 42399980, "avg": 52999980, "max": 63599980},
      "net": {"min": -2799980, "avg": -3499980, "max": -4199980}
    }
  }
}
```
**Note:** Projections show min (80%), avg (100%), max (120%) scenarios

---

## 7. Transaction History
```
GET /api/v1/finance/transactions/
GET /api/v1/finance/transactions/?app=fees&type=income
GET /api/v1/finance/transactions/?from_date=2026-01-01&to_date=2026-01-31

Response:
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "app": "fees",
      "type": "income",
      "amount": 5000,
      "payment_method": "online",
      "description": "Fee collection",
      "date": "2026-01-15"
    }
  ]
}
```

---

## 8. Payment Method Breakdown ⭐ NEW
```
GET /api/v1/finance/reports/payment_methods/

Response:
{
  "breakdown": [
    {"method": "cash", "count": 120, "total": 450000},
    {"method": "bank", "count": 85, "total": 1200000},
    {"method": "online", "count": 200, "total": 2500000},
    {"method": "upi", "count": 50, "total": 150000}
  ]
}
```

---

## 9. Export Summary (Excel/PDF) ⭐ NEW
```
GET /api/v1/finance/reports/export_summary/

Response:
{
  "filename": "finance_summary_20260115",
  "data": [
    {"app": "FEES", "income": 1500000, "expense": 50000, "net": 1450000},
    {"app": "LIBRARY", "income": 25000, "expense": 0, "net": 25000},
    ...
  ],
  "totals": {"income": 2475000, "expense": 2650000, "net": -175000}
}
```
**Usage:** Frontend converts JSON to Excel/PDF

---

## 10. Export Transactions (Excel/PDF) ⭐ NEW
```
GET /api/v1/finance/reports/export_transactions/
GET /api/v1/finance/reports/export_transactions/?from_date=2026-01-01&to_date=2026-01-31

Response:
{
  "filename": "transactions_20260115",
  "count": 250,
  "data": [
    {
      "date": "2026-01-15",
      "app": "fees",
      "type": "income",
      "amount": 5000,
      "payment_method": "online",
      "description": "Fee collection"
    }
  ]
}
```
**Limit:** Max 1000 rows per request

---

## Complete API List

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/other-expenses/` | POST/GET | Create/List expenses |
| 2 | `/other-expenses/{id}/` | GET/PUT/DELETE | Manage expense |
| 3 | `/reports/app_summary/` | GET | App-wise summary |
| 4 | `/reports/totals/` | GET | Overall totals |
| 5 | `/reports/monthly/` | GET | Monthly report |
| 6 | `/reports/dashboard/` | GET | Dashboard stats |
| 7 | `/reports/projections/` | GET | 1/3/5 year projections ⭐ |
| 8 | `/transactions/` | GET | Transaction history |
| 9 | `/reports/payment_methods/` | GET | Payment breakdown ⭐ |
| 10 | `/reports/export_summary/` | GET | Export summary ⭐ |
| 11 | `/reports/export_transactions/` | GET | Export transactions ⭐ |

---

## Authentication
All endpoints require:
```
Authorization: Token <your-token>
```
