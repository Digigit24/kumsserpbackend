# KUMSS ERP - API Guide

## 🚀 Getting Started

The KUMSS ERP API is built with Django REST Framework and documented using drf-spectacular (OpenAPI 3.0).

### Base URL
```
Development: http://localhost:8000/api/v1/
Production: https://api.kumss.edu/api/v1/
```

### API Documentation URLs
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

---

## 🔐 Authentication

### College-Scoped Architecture
All API requests require the `X-College-ID` header (legacy `X-Tenant-ID`) for college identification. Request bodies should not include `tenant_id`; scoping is enforced from the header.

```http
X-College-ID: 1
```
> If you see `tenant_id` in older examples below, treat it as the college ID from this header (it no longer needs to be sent in request bodies).

### Session Authentication
The API uses Django session authentication by default:

```http
POST /api-auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

---

## 📋 API Endpoints Overview

### Core Module (`/api/v1/core/`)

#### Colleges
- `GET /colleges/` - List all colleges
- `POST /colleges/` - Create new college
- `GET /colleges/{id}/` - Get college details
- `PUT /colleges/{id}/` - Update college
- `PATCH /colleges/{id}/` - Partial update
- `DELETE /colleges/{id}/` - Soft delete college
- `GET /colleges/active/` - Get active colleges only
- `POST /colleges/bulk_delete/` - Bulk delete colleges

#### Academic Years
- `GET /academic-years/` - List academic years
- `POST /academic-years/` - Create academic year
- `GET /academic-years/{id}/` - Get details
- `PUT /academic-years/{id}/` - Update
- `PATCH /academic-years/{id}/` - Partial update
- `DELETE /academic-years/{id}/` - Delete
- `GET /academic-years/current/` - Get current academic year

#### Academic Sessions
- `GET /academic-sessions/` - List sessions
- `POST /academic-sessions/` - Create session
- `GET /academic-sessions/{id}/` - Get details
- `PUT /academic-sessions/{id}/` - Update
- `PATCH /academic-sessions/{id}/` - Partial update
- `DELETE /academic-sessions/{id}/` - Delete

#### Holidays
- `GET /holidays/` - List holidays
- `POST /holidays/` - Create holiday
- `GET /holidays/{id}/` - Get details
- `PUT /holidays/{id}/` - Update
- `PATCH /holidays/{id}/` - Partial update
- `DELETE /holidays/{id}/` - Delete

#### Weekends
- `GET /weekends/` - List weekend configurations
- `POST /weekends/` - Create weekend
- `GET /weekends/{id}/` - Get details
- `PUT /weekends/{id}/` - Update
- `PATCH /weekends/{id}/` - Partial update
- `DELETE /weekends/{id}/` - Delete

#### System Settings
- `GET /system-settings/` - List settings
- `POST /system-settings/` - Create settings
- `GET /system-settings/{id}/` - Get details
- `PUT /system-settings/{id}/` - Update
- `PATCH /system-settings/{id}/` - Partial update

#### Notification Settings
- `GET /notification-settings/` - List notification configs
- `POST /notification-settings/` - Create config
- `GET /notification-settings/{id}/` - Get details
- `PUT /notification-settings/{id}/` - Update
- `PATCH /notification-settings/{id}/` - Partial update

#### Activity Logs (Read-Only)
- `GET /activity-logs/` - List activity logs
- `GET /activity-logs/{id}/` - Get log details

---

## 🔍 Filtering & Search

### Query Parameters

All list endpoints support the following query parameters:

#### Pagination
```http
GET /colleges/?page=2&page_size=20
```

#### Filtering
```http
GET /colleges/?is_active=true&state=California
GET /holidays/?college=1&holiday_type=national
GET /academic-sessions/?semester=1&is_current=true
```

#### Search
```http
GET /colleges/?search=MIT
GET /holidays/?search=Christmas
```

#### Ordering
```http
GET /colleges/?ordering=name
GET /colleges/?ordering=-created_at
GET /activity-logs/?ordering=-timestamp
```

---

## 📝 Request Examples

### Create a College

```http
POST /api/v1/core/colleges/
X-Tenant-ID: tenant_001
Content-Type: application/json

{
  "tenant_id": "tenant_001",
  "code": "MIT",
  "name": "Massachusetts Institute of Technology",
  "short_name": "MIT",
  "email": "info@mit.edu",
  "phone": "+1-617-253-1000",
  "address_line1": "77 Massachusetts Avenue",
  "city": "Cambridge",
  "state": "Massachusetts",
  "pincode": "02139",
  "country": "USA",
  "primary_color": "#A31F34",
  "secondary_color": "#8A8B8C",
  "is_main": true,
  "display_order": 1,
  "settings": {
    "academic": {
      "attendance_mandatory_percentage": 75,
      "max_absent_days": 20,
      "grading_system": "CGPA"
    },
    "fees": {
      "late_fee_percentage": 5,
      "installment_allowed": true,
      "discount_allowed": true
    },
    "notifications": {
      "send_birthday_wishes": true,
      "send_result_alerts": true
    },
    "theme": {
      "logo_url": "https://example.com/logo.png",
      "favicon_url": "https://example.com/favicon.ico",
      "primary_font": "Roboto"
    }
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "tenant_id": "tenant_001",
  "code": "MIT",
  "name": "Massachusetts Institute of Technology",
  "short_name": "MIT",
  "email": "info@mit.edu",
  "phone": "+1-617-253-1000",
  "website": null,
  "address_line1": "77 Massachusetts Avenue",
  "address_line2": null,
  "city": "Cambridge",
  "state": "Massachusetts",
  "pincode": "02139",
  "country": "USA",
  "logo": null,
  "established_date": null,
  "affiliation_number": null,
  "primary_color": "#A31F34",
  "secondary_color": "#8A8B8C",
  "settings": { ... },
  "is_main": true,
  "display_order": 1,
  "is_active": true,
  "created_by": { ... },
  "updated_by": { ... },
  "created_at": "2024-12-04T18:30:00Z",
  "updated_at": "2024-12-04T18:30:00Z"
}
```

### Create an Academic Year

```http
POST /api/v1/core/academic-years/
X-Tenant-ID: tenant_001
Content-Type: application/json

{
  "tenant_id": "tenant_001",
  "year": "2025-2026",
  "start_date": "2025-08-01",
  "end_date": "2026-07-31",
  "is_current": true
}
```

### Get Current Academic Year

```http
GET /api/v1/core/academic-years/current/
X-Tenant-ID: tenant_001
```

### Create a Holiday

```http
POST /api/v1/core/holidays/
X-Tenant-ID: tenant_001
Content-Type: application/json

{
  "tenant_id": "tenant_001",
  "college": 1,
  "name": "Independence Day",
  "date": "2025-07-04",
  "holiday_type": "national",
  "description": "National Holiday - Independence Day"
}
```

### Bulk Delete Colleges

```http
POST /api/v1/core/colleges/bulk_delete/
X-Tenant-ID: tenant_001
Content-Type: application/json

{
  "ids": [1, 2, 3, 4, 5]
}
```

---

## 🎯 Special Features

### Automatic Signal Triggers

#### College Creation
When you create a college, the system automatically:
1. Creates a `NotificationSetting` record for the college
2. Creates `Weekend` records for Saturday (5) and Sunday (6)

#### Academic Year
When you set `is_current=true` for an academic year:
- All other academic years for the same tenant are automatically set to `is_current=false`

#### Activity Logs
Activity logs automatically capture:
- Client IP address (handles X-Forwarded-For headers)
- User agent string
- Timestamp and user information

### Soft Delete
Most models support soft delete via the `is_active` flag:
```http
DELETE /api/v1/core/colleges/1/
```
This sets `is_active=false` instead of permanently deleting the record.

---

## 🛠 Error Responses

### Validation Error (400)
```json
{
  "code": {
    "non_field_errors": ["College with this code already exists."]
  }
}
```

### Not Found (404)
```json
{
  "detail": "Not found."
}
```

### Unauthorized (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Permission Denied (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## 📊 Response Format

### List Response (Paginated)
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/core/colleges/?page=2",
  "previous": null,
  "results": [
    { ... },
    { ... }
  ]
}
```

### Detail Response
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2",
  ...
}
```

---

## 🧪 Testing with cURL

### Login
```bash
curl -X POST http://localhost:8000/api-auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  -c cookies.txt
```

### Create College (with cookies)
```bash
curl -X POST http://localhost:8000/api/v1/core/colleges/ \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant_001" \
  -H "X-CSRFToken: your_csrf_token" \
  -b cookies.txt \
  -d @college_data.json
```

---

## 📚 Additional Resources

- **Swagger UI**: Interactive API documentation with try-it-out functionality
- **ReDoc**: Beautiful, responsive API documentation
- **Django Admin**: http://localhost:8000/admin/

---

## 🔧 Development Notes

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Development Server
```bash
python manage.py runserver
```

---

## 📞 Support

For API issues or questions, please contact the development team.
