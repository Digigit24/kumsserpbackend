# KUMSS ERP Statistics Module - Documentation

## Overview
The Statistics Module provides comprehensive analytics endpoints for the KUMSS ERP system. All statistics are computed in real-time from existing data with intelligent caching for optimal performance.

---

## What Has Been Created

### 1. **New Stats App** (`apps/stats/`)

Complete Django app with the following structure:

```
apps/stats/
├── __init__.py
├── apps.py                      # App configuration
├── models.py                    # No database models (computed stats)
├── serializers.py               # Response serializers for all stats
├── views.py                     # ViewSets for all statistics endpoints
├── urls.py                      # URL routing configuration
├── admin.py                     # No admin needed
└── services/                    # Business logic layer
    ├── __init__.py
    ├── academic_stats.py        # Academic performance, attendance, assignments
    ├── financial_stats.py       # Fee collection, expenses, income
    ├── library_stats.py         # Book circulation, fines
    ├── hr_stats.py             # Leave, payroll, staff attendance
    ├── store_stats.py          # Sales, inventory
    ├── hostel_stats.py         # Occupancy, hostel fees
    ├── communication_stats.py  # Messages, events
    └── dashboard_stats.py      # Dashboard overview
```

---

## Files Created/Modified

### **Files Created:**

1. **`apps/stats/apps.py`** - App configuration
2. **`apps/stats/models.py`** - Empty (stats are computed, not stored)
3. **`apps/stats/admin.py`** - Empty (no admin needed)
4. **`apps/stats/serializers.py`** - All response serializers (40+ serializers)
5. **`apps/stats/views.py`** - 8 ViewSets with multiple endpoints
6. **`apps/stats/urls.py`** - URL routing
7. **`apps/stats/services/academic_stats.py`** - Academic statistics service
8. **`apps/stats/services/financial_stats.py`** - Financial statistics service
9. **`apps/stats/services/library_stats.py`** - Library statistics service
10. **`apps/stats/services/hr_stats.py`** - HR statistics service
11. **`apps/stats/services/store_stats.py`** - Store statistics service
12. **`apps/stats/services/hostel_stats.py`** - Hostel statistics service
13. **`apps/stats/services/communication_stats.py`** - Communication statistics service
14. **`apps/stats/services/dashboard_stats.py`** - Dashboard statistics service

### **Files Modified:**

1. **`kumss_erp/urls.py`** (Line 43) - Added stats URL routing:
   ```python
   path('api/v1/stats/', include('apps.stats.urls', namespace='stats')),
   ```

2. **`kumss_erp/settings/base.py`** (Line 65) - Added to INSTALLED_APPS:
   ```python
   'apps.stats',
   ```

---

## API Endpoints

All endpoints follow the pattern: `/api/v1/stats/{module}/`

### **Base URL:** `/api/v1/stats/`

### **Available Endpoints:**

| Endpoint | Method | Description | Cache Time |
|----------|--------|-------------|------------|
| `/api/v1/stats/dashboard/` | GET | Complete dashboard overview | 5 min |
| `/api/v1/stats/academic/` | GET | All academic statistics | 15 min |
| `/api/v1/stats/academic/performance/` | GET | Performance stats only | Real-time |
| `/api/v1/stats/academic/attendance/` | GET | Attendance stats only | Real-time |
| `/api/v1/stats/academic/assignments/` | GET | Assignment stats only | Real-time |
| `/api/v1/stats/financial/` | GET | All financial statistics | 15 min |
| `/api/v1/stats/financial/fee_collection/` | GET | Fee collection only | Real-time |
| `/api/v1/stats/financial/expenses/` | GET | Expense stats only | Real-time |
| `/api/v1/stats/financial/income/` | GET | Income stats only | Real-time |
| `/api/v1/stats/library/` | GET | Library circulation stats | 15 min |
| `/api/v1/stats/hr/` | GET | All HR statistics | 15 min |
| `/api/v1/stats/store/` | GET | Store sales statistics | 15 min |
| `/api/v1/stats/store/inventory/` | GET | Inventory stats only | Real-time |
| `/api/v1/stats/hostel/` | GET | Hostel occupancy stats | 15 min |
| `/api/v1/stats/hostel/fees/` | GET | Hostel fee stats | Real-time |
| `/api/v1/stats/communication/` | GET | Communication stats | 15 min |

---

## Query Parameters (Filters)

All endpoints support the following query parameters:

| Parameter | Type | Format | Description | Example |
|-----------|------|--------|-------------|---------|
| `from_date` | Date | YYYY-MM-DD | Start date for filtering | `2024-01-01` |
| `to_date` | Date | YYYY-MM-DD | End date for filtering | `2024-12-31` |
| `academic_year` | Integer | ID | Filter by academic year | `1` |
| `program` | Integer | ID | Filter by program | `3` |
| `class` | Integer | ID | Filter by class | `10` |
| `section` | Integer | ID | Filter by section | `5` |
| `department` | Integer | ID | Filter by department | `2` |
| `month` | Integer | 1-12 | Filter by month (for payroll) | `10` |
| `year` | Integer | YYYY | Filter by year (for payroll) | `2024` |

### **Example Usage:**

```bash
# Get academic stats for a specific class
GET /api/v1/stats/academic/?class=10&from_date=2024-01-01&to_date=2024-12-31

# Get financial stats for a program
GET /api/v1/stats/financial/?program=3&from_date=2024-01-01

# Get HR stats for a department
GET /api/v1/stats/hr/?department=2&month=10&year=2024
```

---

## Request/Response Flow

### **1. Request Flow:**

```
Frontend Request
    ↓
X-College-ID Header Validation (CollegeMiddleware)
    ↓
ViewSet.list() or custom action
    ↓
Check Cache (cache_key = "module:college_id:filters_hash")
    ↓
If Cached: Return cached data
    ↓
If Not Cached:
    ↓
Parse Filters (from query params)
    ↓
Service Layer (AcademicStatsService, FinancialStatsService, etc.)
    ↓
Database Queries (with college scoping)
    ↓
Calculate Statistics
    ↓
Serialize Response
    ↓
Cache Result (5-15 minutes)
    ↓
Return Response
```

### **2. Service Layer Architecture:**

Each service class follows this pattern:

```python
class AcademicStatsService:
    def __init__(self, college_id, filters=None):
        self.college_id = college_id
        self.filters = filters or {}

    def get_performance_stats(self):
        # Calculate performance statistics
        # Returns: dict

    def get_attendance_stats(self):
        # Calculate attendance statistics
        # Returns: dict

    def get_all_stats(self):
        # Combine all statistics
        # Returns: dict
```

### **3. Caching Strategy:**

- **Dashboard Stats**: 5 minutes (frequently updated)
- **Module Stats**: 15 minutes (less frequent updates)
- **Cache Key Format**: `{module}:{college_id}:{filters_hash}`
- **Cache Backend**: Django Cache (can be configured for Redis)

---

## Example API Responses

### **Dashboard Overview:**

```json
GET /api/v1/stats/dashboard/

{
  "total_students": 1250,
  "total_teachers": 85,
  "total_staff": 30,
  "active_classes": 45,
  "today_student_attendance_rate": 92.5,
  "today_staff_attendance_rate": 95.0,
  "today_present_students": 1156,
  "today_absent_students": 94,
  "total_fee_collected_this_month": "1250000.00",
  "total_fee_outstanding": "350000.00",
  "total_expenses_this_month": "180000.00",
  "average_student_performance": 75.5,
  "upcoming_exams": 5,
  "pending_assignments": 23,
  "books_issued_today": 45,
  "overdue_books": 12,
  "recent_admissions": 8,
  "recent_fee_payments": 156,
  "generated_at": "2024-12-29T10:30:00Z"
}
```

### **Academic Statistics:**

```json
GET /api/v1/stats/academic/?class=10&from_date=2024-01-01&to_date=2024-12-31

{
  "performance": {
    "total_students": 120,
    "total_exams_conducted": 8,
    "average_percentage": 75.5,
    "pass_percentage": 92.0,
    "pass_count": 110,
    "fail_count": 10,
    "grade_distribution": [
      {"grade": "A+", "count": 25, "percentage": 20.8},
      {"grade": "A", "count": 45, "percentage": 37.5},
      {"grade": "B+", "count": 30, "percentage": 25.0}
    ],
    "top_performers": [
      {
        "student_id": 1,
        "admission_number": "2024001",
        "student_name": "John Doe",
        "percentage": 95.5,
        "grade": "A+",
        "rank": 1
      }
    ]
  },
  "attendance": {
    "total_records": 3600,
    "present_count": 3330,
    "absent_count": 180,
    "late_count": 90,
    "leave_count": 0,
    "attendance_rate": 92.5,
    "chronic_absentees_count": 5,
    "perfect_attendance_count": 35,
    "daily_trend": [
      {
        "date": "2024-01-15",
        "total": 120,
        "present": 112,
        "absent": 8,
        "late": 0,
        "attendance_rate": 93.3
      }
    ]
  },
  "assignments": {
    "total_assignments": 45,
    "total_submissions": 5400,
    "submitted_count": 5100,
    "pending_count": 200,
    "graded_count": 4800,
    "late_submissions": 300,
    "submission_rate": 94.4,
    "average_marks": 78.5,
    "completion_rate": 88.9
  },
  "subject_wise_performance": [
    {
      "subject_id": 1,
      "subject_name": "Mathematics",
      "subject_code": "MATH101",
      "average_marks": 72.5,
      "pass_percentage": 88.0,
      "total_students": 120
    }
  ],
  "generated_at": "2024-12-29T10:30:00Z"
}
```

### **Financial Statistics:**

```json
GET /api/v1/stats/financial/?from_date=2024-01-01&to_date=2024-12-31

{
  "fee_collection": {
    "total_students": 1250,
    "total_fee_amount": "18750000.00",
    "total_collected": "16500000.00",
    "total_outstanding": "2250000.00",
    "collection_rate": 88.0,
    "defaulters_count": 145,
    "fully_paid_count": 1105,
    "payment_method_distribution": [
      {
        "payment_method": "CASH",
        "count": 856,
        "total_amount": "8250000.00",
        "percentage": 50.0
      },
      {
        "payment_method": "ONLINE",
        "count": 680,
        "total_amount": "6800000.00",
        "percentage": 39.8
      }
    ],
    "monthly_trend": [
      {
        "month": "January",
        "year": 2024,
        "total_collected": "1500000.00",
        "total_due": "1800000.00",
        "collection_rate": 83.3
      }
    ]
  },
  "expenses": {
    "total_expenses": "2850000.00",
    "total_transactions": 456,
    "average_expense": "6250.00",
    "category_breakdown": [
      {
        "category_id": 1,
        "category_name": "Salaries",
        "total_amount": "2000000.00",
        "transaction_count": 85,
        "percentage": 70.2
      }
    ]
  },
  "income": {
    "total_income": "450000.00",
    "total_transactions": 78,
    "average_income": "5769.23",
    "category_breakdown": [
      {
        "category_id": 1,
        "category_name": "Transportation",
        "total_amount": "250000.00",
        "transaction_count": 45,
        "percentage": 55.6
      }
    ]
  },
  "net_balance": "14100000.00",
  "generated_at": "2024-12-29T10:30:00Z"
}
```

---

## Frontend Integration Guide

### **1. API Call Example (JavaScript/Axios):**

```javascript
// Get dashboard stats
const getDashboardStats = async () => {
  try {
    const response = await axios.get('/api/v1/stats/dashboard/', {
      headers: {
        'Authorization': `Token ${authToken}`,
        'X-College-ID': collegeId
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
  }
};

// Get academic stats with filters
const getAcademicStats = async (classId, fromDate, toDate) => {
  try {
    const response = await axios.get('/api/v1/stats/academic/', {
      headers: {
        'Authorization': `Token ${authToken}`,
        'X-College-ID': collegeId
      },
      params: {
        class: classId,
        from_date: fromDate,
        to_date: toDate
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching academic stats:', error);
  }
};

// Get financial stats
const getFinancialStats = async (programId, fromDate, toDate) => {
  try {
    const response = await axios.get('/api/v1/stats/financial/', {
      headers: {
        'Authorization': `Token ${authToken}`,
        'X-College-ID': collegeId
      },
      params: {
        program: programId,
        from_date: fromDate,
        to_date: toDate
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching financial stats:', error);
  }
};
```

### **2. React Component Example:**

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DashboardStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/v1/stats/dashboard/', {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'X-College-ID': localStorage.getItem('collegeId')
          }
        });
        setStats(response.data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard-stats">
      <div className="stat-card">
        <h3>Total Students</h3>
        <p>{stats?.total_students}</p>
      </div>
      <div className="stat-card">
        <h3>Today's Attendance</h3>
        <p>{stats?.today_student_attendance_rate}%</p>
      </div>
      <div className="stat-card">
        <h3>Fee Collected (This Month)</h3>
        <p>₹{stats?.total_fee_collected_this_month}</p>
      </div>
      {/* More stats... */}
    </div>
  );
};

export default DashboardStats;
```

---

## Statistics Fields Summary

### **Dashboard:**
- Total students, teachers, staff, classes
- Today's attendance rates
- Financial summary (collected, outstanding, expenses)
- Academic performance average
- Upcoming exams, pending assignments
- Library activity (books issued, overdue)
- Recent activities (admissions, payments)

### **Academic:**
- **Performance**: Total students, exams, average %, pass %, grade distribution, top performers
- **Attendance**: Total records, present/absent/late counts, attendance rate, chronic absentees, daily trends
- **Assignments**: Total assignments, submissions, graded count, late submissions, average marks
- **Subject-wise**: Average marks, pass percentage per subject

### **Financial:**
- **Fee Collection**: Total amount, collected, outstanding, collection rate, defaulters, payment methods, monthly trends
- **Expenses**: Total expenses, transaction count, category breakdown
- **Income**: Total income, transaction count, category breakdown
- **Net Balance**: Total income - total expenses

### **Library:**
- Total books, available, issued, overdue
- Total fines (collected, outstanding)
- Popular books with issue counts
- Active members

### **HR:**
- **Leave**: Applications, approvals, pending, rejected, leave type distribution
- **Payroll**: Total employees, gross salary, deductions, net salary, payment status
- **Staff Attendance**: Present/absent/late counts, attendance rate

### **Store:**
- **Sales**: Total sales, revenue, items sold, popular items, payment methods
- **Inventory**: Total items, low stock alerts, out of stock, inventory value

### **Hostel:**
- **Occupancy**: Total hostels/rooms/beds, occupied/vacant, occupancy rate
- **Fees**: Total amount, collected, outstanding, collection rate

### **Communication:**
- **Messages**: Total sent, delivered, failed, pending, delivery rate
- **Events**: Total events, upcoming, completed, registrations, attendance

---

## Performance Considerations

### **Caching:**
- All stats endpoints use Django cache
- Cache keys include college_id and filters for isolation
- Default cache times: 5-15 minutes
- Can be configured for Redis for better performance

### **Query Optimization:**
- Uses `select_related()` for FK lookups
- Uses `prefetch_related()` for M2M lookups
- Aggregates at database level using Django ORM
- Filters applied before aggregation

### **College Scoping:**
- All queries automatically filtered by `college_id`
- Uses thread-local college context from `CollegeMiddleware`
- Ensures data isolation between colleges

---

## Testing the Implementation

### **1. Start Development Server:**

```bash
# Activate virtual environment (if exists)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run migrations (if needed)
python manage.py makemigrations
python manage.py migrate

# Start server
python manage.py runserver
```

### **2. Access API Documentation:**

```
# Swagger UI
http://localhost:8000/api/docs/

# ReDoc
http://localhost:8000/api/redoc/

# OpenAPI Schema
http://localhost:8000/api/schema/
```

### **3. Test Endpoints (with curl):**

```bash
# Get dashboard stats
curl -X GET "http://localhost:8000/api/v1/stats/dashboard/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "X-College-ID: 1"

# Get academic stats with filters
curl -X GET "http://localhost:8000/api/v1/stats/academic/?class=10&from_date=2024-01-01" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "X-College-ID: 1"

# Get financial stats
curl -X GET "http://localhost:8000/api/v1/stats/financial/?from_date=2024-01-01&to_date=2024-12-31" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "X-College-ID: 1"
```

---

## Extending the Stats Module

### **Adding New Statistics:**

1. **Create new method in service class:**

```python
# In apps/stats/services/academic_stats.py
def get_homework_stats(self):
    """Calculate homework statistics"""
    # Your logic here
    return {
        'total_homework': 100,
        'completion_rate': 85.5,
        # ... more stats
    }
```

2. **Create serializer:**

```python
# In apps/stats/serializers.py
class HomeworkStatsSerializer(serializers.Serializer):
    total_homework = serializers.IntegerField()
    completion_rate = serializers.FloatField()
```

3. **Add action to ViewSet:**

```python
# In apps/stats/views.py
@action(detail=False, methods=['get'])
def homework(self, request):
    """Get homework statistics"""
    college_id = self.get_college_id()
    filters = self.parse_filters(request)

    service = AcademicStatsService(college_id, filters)
    data = service.get_homework_stats()

    return Response(data)
```

4. **Access new endpoint:**
```
GET /api/v1/stats/academic/homework/
```

---

## Troubleshooting

### **Common Issues:**

1. **Missing X-College-ID Header:**
   - Error: "X-College-ID header is required"
   - Solution: Always include `X-College-ID` header in requests

2. **Cache Not Updating:**
   - Solution: Clear cache manually or wait for expiration
   ```python
   from django.core.cache import cache
   cache.clear()
   ```

3. **Slow Performance:**
   - Enable Redis caching in settings
   - Check database indexes on frequently queried fields
   - Review query optimization in service layer

4. **No Data Returned:**
   - Check if data exists for the given filters
   - Verify college_id is correct
   - Check date range filters

---

## Summary

The Statistics Module provides:

✅ **8 Main Endpoints** for different modules
✅ **40+ Serializers** for structured responses
✅ **8 Service Classes** with clean business logic
✅ **Intelligent Caching** for performance
✅ **College Scoping** for data isolation
✅ **Flexible Filtering** via query parameters
✅ **OpenAPI Documentation** auto-generated
✅ **Frontend-Ready** JSON responses

All statistics are computed in real-time from existing data with no additional database models required. The module follows KUMSS ERP's architecture patterns and integrates seamlessly with the existing codebase.

---

## Support

For issues or questions, please:
1. Check the API documentation at `/api/docs/`
2. Review this documentation
3. Check Django logs for errors
4. Verify database connectivity and data

---

**Created**: December 29, 2024
**Version**: 1.0
**Author**: KUMSS ERP Development Team
