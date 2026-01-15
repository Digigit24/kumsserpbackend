# Finance API Reference

Base URL: `/api/v1/finance/`

## 1. Other Expenses

### Create Expense
```
POST /api/v1/finance/other-expenses/
{
  "title": "Office Supplies",
  "description": "Monthly stationery",
  "amount": 5000.00,
  "category": "supplies",
  "date": "2026-01-15"
}
```

### List Expenses
```
GET /api/v1/finance/other-expenses/
```

### Get Single Expense
```
GET /api/v1/finance/other-expenses/{id}/
```

### Update Expense
```
PUT /api/v1/finance/other-expenses/{id}/
```

### Delete Expense
```
DELETE /api/v1/finance/other-expenses/{id}/
```

---

## 2. App-wise Summary

```
GET /api/v1/finance/reports/app_summary/

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

## 6. Transaction History

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
      "description": "Fee collection",
      "reference_id": 123,
      "reference_model": "FeeCollection",
      "date": "2026-01-15",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

---

## Categories for Other Expenses

- `maintenance`
- `utilities`
- `supplies`
- `marketing`
- `travel`
- `miscellaneous`

---

## Authentication

All endpoints require:
```
Authorization: Token <your-token>
```
