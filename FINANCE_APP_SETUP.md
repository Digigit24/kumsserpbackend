# Finance App Setup Guide

## Overview
Complete backend implementation for finance module to track all money-related transactions across the system.

## Installation Steps

### 1. Run Migrations
```bash
python manage.py makemigrations finance
python manage.py migrate finance
```

### 2. Initial Data Sync
Sync existing transactions from all apps to finance module:
```bash
python manage.py sync_finance_data
```

To clear existing data and resync:
```bash
python manage.py sync_finance_data --clear
```

## API Endpoints

Base URL: `/api/v1/finance/`

### Core CRUD Endpoints
- `GET/POST /app-income/` - App income records
- `GET/POST /app-expense/` - App expense records
- `GET/POST /app-total/` - App totals
- `GET/POST /finance-total/` - Overall finance totals
- `GET/POST/PUT/DELETE /other-expenses/` - Other expenses

### Transaction History
- `GET /transactions/` - View all transactions
  - Query params: `?app=fees&type=income&from_date=2026-01-01&to_date=2026-01-31`

### Reports & Analytics
- `GET /reports/app_summary/` - App-wise income/expense summary
- `GET /reports/totals/` - Overall finance totals
- `GET /reports/monthly/?year=2026&month=1` - Monthly report
- `GET /reports/dashboard/` - Dashboard statistics

## Auto-Sync Configuration

Finance app automatically syncs data using Django signals when:

### Income Sources
1. **Fees App**
   - FeeCollection created → fees income
   - FeeFine created → fees income

2. **Library App**
   - LibraryFine created → library income

3. **Hostel App**
   - HostelFee created → hostel income

4. **Store App**
   - StoreSale created → store income

### Expense Sources
1. **Fees App**
   - FeeRefund created → fees expense

2. **HR App**
   - Payroll created → hr expense

3. **Store App**
   - PurchaseOrder created → store expense

4. **Finance App**
   - OtherExpense created → other expense

## Models

### AppIncome
- Tracks income per app per month
- Fields: app_name, month, amount, transaction_count

### AppExpense
- Tracks expense per app per month
- Fields: app_name, month, amount, transaction_count

### AppTotal
- Net total per app per month (income - expense)
- Fields: app_name, month, income, expense, net_total

### FinanceTotal
- Overall finance totals per month
- Fields: month, total_income, total_expense, net_total

### OtherExpense
- Additional expenses not covered by other apps
- Fields: title, description, amount, category, date, receipt, created_by

### FinanceTransaction
- Unified transaction log
- Fields: app, type, amount, description, reference_id, reference_model, date

## Permissions
- All endpoints require authentication (`IsAuthenticated`)
- Recommended: Admin/Finance Manager roles only

## Testing

### Create Sample Data
```python
from finance.models import OtherExpense
from datetime import date

OtherExpense.objects.create(
    title="Office Supplies",
    description="Monthly stationery purchase",
    amount=5000.00,
    category="supplies",
    date=date.today(),
    created_by=user
)
```

### Check Auto-Sync
```python
# Create a fee collection
from fees.models import FeeCollection

collection = FeeCollection.objects.create(
    student=student,
    amount=10000,
    payment_date=date.today()
)

# Check finance app
from finance.models import AppIncome
AppIncome.objects.filter(app_name='fees')
```

## Troubleshooting

### Signals Not Working
Check if `finance.apps.FinanceConfig.ready()` is loading signals:
```python
# In finance/apps.py
def ready(self):
    import finance.signals  # Must be present
```

### Missing Transactions
Run manual sync:
```bash
python manage.py sync_finance_data
```

### Database Issues
Check migrations:
```bash
python manage.py showmigrations finance
```

## Celery Task (Optional)
For periodic sync, add to Celery beat:
```python
# In celery.py
@periodic_task(run_every=crontab(hour='*/1'))  # Every hour
def sync_finance():
    from django.core.management import call_command
    call_command('sync_finance_data')
```

## Frontend Integration
See `finance frontend.md` for complete API documentation and flow for frontend developers.
