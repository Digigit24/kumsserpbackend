# Core App - API Documentation for Frontend Integration

## 📌 Overview

This document provides comprehensive API documentation for the **Core App** module of KUMSS ERP. All endpoints require authentication and multi-tenant header.

**Base URL**: `/api/v1/core/`

---

## 🔐 Authentication & Headers

### Required Headers

All API requests must include:

```http
X-College-ID: <college_pk>   # legacy header name X-Tenant-ID is still accepted
Content-Type: application/json
Cookie: sessionid=your_session_cookie
X-CSRFToken: your_csrf_token
```

> College guard: `X-College-ID` is mandatory (legacy: `X-Tenant-ID`). The backend now scopes purely by college and request bodies should not include `tenant_id`—treat any remaining `tenant_id` references in this document as legacy aliases for the college ID header.

### Authentication Endpoints

#### Login
```http
POST /api-auth/login/
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response:**
- Sets `sessionid` cookie
- Returns CSRF token in response headers

#### Logout
```http
POST /api-auth/logout/
```

---

## 📚 API Endpoints

### 1. Colleges API

Base path: `/api/v1/core/colleges/`

#### 1.1 List All Colleges

```http
GET /api/v1/core/colleges/
```

**Query Parameters:**
- `page` (integer) - Page number (default: 1)
- `page_size` (integer) - Items per page (default: 20)
- `is_active` (boolean) - Filter by active status
- `is_main` (boolean) - Filter main university
- `state` (string) - Filter by state
- `country` (string) - Filter by country
- `search` (string) - Search in name, code, city, email
- `ordering` (string) - Sort by field (prefix with `-` for descending)
  - Options: `name`, `code`, `display_order`, `created_at`, `-name`, etc.

**Example Request:**
```javascript
fetch('/api/v1/core/colleges/?is_active=true&search=MIT&ordering=name', {
  method: 'GET',
  headers: {
    'X-Tenant-ID': 'tenant_001',
    'Content-Type': 'application/json'
  },
  credentials: 'include'
})
```

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/v1/core/colleges/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "MIT",
      "name": "Massachusetts Institute of Technology",
      "short_name": "MIT",
      "city": "Cambridge",
      "state": "Massachusetts",
      "country": "USA",
      "is_main": true,
      "is_active": true
    }
  ]
}
```

#### 1.2 Get College Details

```http
GET /api/v1/core/colleges/{id}/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "tenant_id": "tenant_001",
  "code": "MIT",
  "name": "Massachusetts Institute of Technology",
  "short_name": "MIT",
  "email": "info@mit.edu",
  "phone": "+1-617-253-1000",
  "website": "https://www.mit.edu",
  "address_line1": "77 Massachusetts Avenue",
  "address_line2": null,
  "city": "Cambridge",
  "state": "Massachusetts",
  "pincode": "02139",
  "country": "USA",
  "logo": "/media/college_logos/mit_logo.png",
  "established_date": "1861-04-10",
  "affiliation_number": "MIT-001",
  "primary_color": "#A31F34",
  "secondary_color": "#8A8B8C",
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
  },
  "is_main": true,
  "display_order": 1,
  "is_active": true,
  "created_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@kumss.edu",
    "first_name": "Admin",
    "last_name": "User"
  },
  "updated_by": {
    "id": 1,
    "username": "admin",
    "email": "admin@kumss.edu",
    "first_name": "Admin",
    "last_name": "User"
  },
  "created_at": "2024-12-04T10:30:00Z",
  "updated_at": "2024-12-04T15:45:00Z"
}
```

#### 1.3 Create New College

```http
POST /api/v1/core/colleges/
```

**Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "code": "HARVARD",
  "name": "Harvard University",
  "short_name": "Harvard",
  "email": "info@harvard.edu",
  "phone": "+1-617-495-1000",
  "website": "https://www.harvard.edu",
  "address_line1": "Massachusetts Hall",
  "address_line2": "Harvard Yard",
  "city": "Cambridge",
  "state": "Massachusetts",
  "pincode": "02138",
  "country": "USA",
  "established_date": "1636-09-08",
  "affiliation_number": "HARV-001",
  "primary_color": "#A51C30",
  "secondary_color": "#000000",
  "settings": {
    "academic": {
      "attendance_mandatory_percentage": 80,
      "max_absent_days": 15,
      "grading_system": "GPA"
    },
    "fees": {
      "late_fee_percentage": 10,
      "installment_allowed": true,
      "discount_allowed": false
    },
    "notifications": {
      "send_birthday_wishes": true,
      "send_result_alerts": true
    },
    "theme": {
      "logo_url": "https://example.com/harvard_logo.png",
      "favicon_url": "https://example.com/harvard_favicon.ico",
      "primary_font": "Georgia"
    }
  },
  "is_main": false,
  "display_order": 2,
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "tenant_id": "tenant_001",
  "code": "HARVARD",
  "name": "Harvard University",
  ...
}
```

**Note:** Creating a college automatically creates:
- Default NotificationSetting record
- Weekend records for Saturday and Sunday

#### 1.4 Update College

```http
PUT /api/v1/core/colleges/{id}/
```

**Request Body:** (All fields required)
```json
{
  "tenant_id": "tenant_001",
  "code": "HARVARD",
  "name": "Harvard University - Updated",
  ...
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "tenant_id": "tenant_001",
  "code": "HARVARD",
  "name": "Harvard University - Updated",
  ...
}
```

#### 1.5 Partial Update College

```http
PATCH /api/v1/core/colleges/{id}/
```

**Request Body:** (Only fields to update)
```json
{
  "email": "newemail@harvard.edu",
  "phone": "+1-617-495-2000"
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "email": "newemail@harvard.edu",
  "phone": "+1-617-495-2000",
  ...
}
```

#### 1.6 Delete College (Soft Delete)

```http
DELETE /api/v1/core/colleges/{id}/
```

**Response (204 No Content)**

**Note:** This performs a soft delete (sets `is_active=false`)

#### 1.7 Get Active Colleges Only

```http
GET /api/v1/core/colleges/active/
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "code": "MIT",
    "name": "Massachusetts Institute of Technology",
    ...
  }
]
```

#### 1.8 Bulk Delete Colleges

```http
POST /api/v1/core/colleges/bulk_delete/
```

**Request Body:**
```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

**Response (200 OK):**
```json
{
  "message": "5 colleges deleted successfully",
  "deleted_ids": [1, 2, 3, 4, 5]
}
```

---

### 2. Academic Years API

Base path: `/api/v1/core/academic-years/`

#### 2.1 List Academic Years

```http
GET /api/v1/core/academic-years/
```

**Query Parameters:**
- `page` (integer) - Page number
- `page_size` (integer) - Items per page
- `is_current` (boolean) - Filter current year
- `is_active` (boolean) - Filter active years
- `search` (string) - Search in year label
- `ordering` (string) - Sort by `start_date`, `year`, etc.

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": "tenant_001",
      "year": "2025-2026",
      "start_date": "2025-08-01",
      "end_date": "2026-07-31",
      "is_current": true,
      "is_active": true,
      "created_by": {...},
      "updated_by": {...},
      "created_at": "2024-12-04T10:00:00Z",
      "updated_at": "2024-12-04T10:00:00Z"
    }
  ]
}
```

#### 2.2 Get Academic Year Details

```http
GET /api/v1/core/academic-years/{id}/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "tenant_id": "tenant_001",
  "year": "2025-2026",
  "start_date": "2025-08-01",
  "end_date": "2026-07-31",
  "is_current": true,
  "is_active": true,
  "created_by": {...},
  "updated_by": {...},
  "created_at": "2024-12-04T10:00:00Z",
  "updated_at": "2024-12-04T10:00:00Z"
}
```

#### 2.3 Create Academic Year

```http
POST /api/v1/core/academic-years/
```

**Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "year": "2026-2027",
  "start_date": "2026-08-01",
  "end_date": "2027-07-31",
  "is_current": false,
  "is_active": true
}
```

**Validation Rules:**
- `end_date` must be after `start_date`
- `year` must be unique per tenant

**Response (201 Created):**
```json
{
  "id": 2,
  "tenant_id": "tenant_001",
  "year": "2026-2027",
  ...
}
```

**Important:** If `is_current=true`, all other years are automatically set to `is_current=false`

#### 2.4 Update Academic Year

```http
PUT /api/v1/core/academic-years/{id}/
PATCH /api/v1/core/academic-years/{id}/
```

**Request Body (PATCH example):**
```json
{
  "is_current": true
}
```

**Response (200 OK):**
```json
{
  "id": 2,
  "is_current": true,
  ...
}
```

#### 2.5 Delete Academic Year

```http
DELETE /api/v1/core/academic-years/{id}/
```

**Response (204 No Content)**

#### 2.6 Get Current Academic Year

```http
GET /api/v1/core/academic-years/current/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "tenant_id": "tenant_001",
  "year": "2025-2026",
  "start_date": "2025-08-01",
  "end_date": "2026-07-31",
  "is_current": true,
  "is_active": true,
  ...
}
```

**Error (404 Not Found):**
```json
{
  "error": "No current academic year found"
}
```

---

### 3. Academic Sessions API

Base path: `/api/v1/core/academic-sessions/`

#### 3.1 List Academic Sessions

```http
GET /api/v1/core/academic-sessions/
```

**Query Parameters:**
- `college` (integer) - Filter by college ID
- `academic_year` (integer) - Filter by academic year ID
- `semester` (integer) - Filter by semester (1-8)
- `is_current` (boolean) - Filter current session
- `is_active` (boolean) - Filter active sessions
- `search` (string) - Search in session name

**Response (200 OK):**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": "tenant_001",
      "college": 1,
      "college_name": "Massachusetts Institute of Technology",
      "academic_year": 1,
      "academic_year_label": "2025-2026",
      "name": "Fall Semester 2025",
      "semester": 1,
      "start_date": "2025-08-01",
      "end_date": "2025-12-20",
      "is_current": true,
      "is_active": true,
      "created_by": {...},
      "updated_by": {...},
      "created_at": "2024-12-04T10:00:00Z",
      "updated_at": "2024-12-04T10:00:00Z"
    }
  ]
}
```

#### 3.2 Create Academic Session

```http
POST /api/v1/core/academic-sessions/
```

**Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "college": 1,
  "academic_year": 1,
  "name": "Spring Semester 2026",
  "semester": 2,
  "start_date": "2026-01-15",
  "end_date": "2026-05-30",
  "is_current": false,
  "is_active": true
}
```

**Validation Rules:**
- `semester` must be between 1 and 8
- `end_date` must be after `start_date`
- Combination of `tenant_id`, `college`, `academic_year`, `semester` must be unique

**Response (201 Created):**
```json
{
  "id": 2,
  "tenant_id": "tenant_001",
  "college": 1,
  "college_name": "Massachusetts Institute of Technology",
  "academic_year": 1,
  "academic_year_label": "2025-2026",
  "name": "Spring Semester 2026",
  "semester": 2,
  ...
}
```

#### 3.3 Update/Delete Operations

Same pattern as Academic Years:
- `PUT /api/v1/core/academic-sessions/{id}/` - Full update
- `PATCH /api/v1/core/academic-sessions/{id}/` - Partial update
- `DELETE /api/v1/core/academic-sessions/{id}/` - Delete

---

### 4. Holidays API

Base path: `/api/v1/core/holidays/`

#### 4.1 List Holidays

```http
GET /api/v1/core/holidays/
```

**Query Parameters:**
- `college` (integer) - Filter by college ID
- `holiday_type` (string) - Filter by type: `national`, `festival`, `college`, `exam`
- `date` (date) - Filter by specific date (YYYY-MM-DD)
- `is_active` (boolean) - Filter active holidays
- `search` (string) - Search in name, description

**Response (200 OK):**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": "tenant_001",
      "college": 1,
      "college_name": "MIT",
      "name": "Independence Day",
      "date": "2025-07-04",
      "holiday_type": "national",
      "holiday_type_display": "National Holiday",
      "description": "National Holiday - Independence Day",
      "is_active": true,
      "created_by": {...},
      "updated_by": {...},
      "created_at": "2024-12-04T10:00:00Z",
      "updated_at": "2024-12-04T10:00:00Z"
    }
  ]
}
```

#### 4.2 Create Holiday

```http
POST /api/v1/core/holidays/
```

**Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "college": 1,
  "name": "Christmas Day",
  "date": "2025-12-25",
  "holiday_type": "festival",
  "description": "Christmas celebration",
  "is_active": true
}
```

**Holiday Types:**
- `national` - National Holiday
- `festival` - Festival
- `college` - College Holiday
- `exam` - Exam Holiday

**Response (201 Created):**
```json
{
  "id": 2,
  "tenant_id": "tenant_001",
  "college": 1,
  "college_name": "MIT",
  "name": "Christmas Day",
  "date": "2025-12-25",
  "holiday_type": "festival",
  "holiday_type_display": "Festival",
  "description": "Christmas celebration",
  "is_active": true,
  ...
}
```

#### 4.3 Update/Delete Operations

- `GET /api/v1/core/holidays/{id}/` - Get details
- `PUT /api/v1/core/holidays/{id}/` - Full update
- `PATCH /api/v1/core/holidays/{id}/` - Partial update
- `DELETE /api/v1/core/holidays/{id}/` - Delete

---

### 5. Weekends API

Base path: `/api/v1/core/weekends/`

#### 5.1 List Weekend Configurations

```http
GET /api/v1/core/weekends/
```

**Query Parameters:**
- `college` (integer) - Filter by college ID
- `day` (integer) - Filter by day (0-6)
- `is_active` (boolean) - Filter active weekends

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": "tenant_001",
      "college": 1,
      "college_name": "MIT",
      "day": 5,
      "day_display": "Saturday",
      "is_active": true,
      "created_by": {...},
      "updated_by": {...},
      "created_at": "2024-12-04T10:00:00Z",
      "updated_at": "2024-12-04T10:00:00Z"
    },
    {
      "id": 2,
      "tenant_id": "tenant_001",
      "college": 1,
      "college_name": "MIT",
      "day": 6,
      "day_display": "Sunday",
      "is_active": true,
      ...
    }
  ]
}
```

#### 5.2 Create Weekend Configuration

```http
POST /api/v1/core/weekends/
```

**Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "college": 1,
  "day": 4,
  "is_active": true
}
```

**Day Values:**
- `0` - Monday
- `1` - Tuesday
- `2` - Wednesday
- `3` - Thursday
- `4` - Friday
- `5` - Saturday
- `6` - Sunday

**Validation Rules:**
- Combination of `tenant_id`, `college`, `day` must be unique

**Response (201 Created):**
```json
{
  "id": 3,
  "tenant_id": "tenant_001",
  "college": 1,
  "college_name": "MIT",
  "day": 4,
  "day_display": "Friday",
  "is_active": true,
  ...
}
```

---

### 6. System Settings API

Base path: `/api/v1/core/system-settings/`

#### 6.1 List System Settings

```http
GET /api/v1/core/system-settings/
```

**Query Parameters:**
- `is_active` (boolean) - Filter active settings

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": "tenant_001",
      "settings": {
        "system": {
          "app_name": "KUMSS ERP",
          "version": "1.0.0",
          "timezone": "America/New_York",
          "date_format": "MM/DD/YYYY",
          "currency": "USD",
          "language": "en"
        },
        "email": {
          "from_address": "noreply@kumss.edu",
          "smtp_host": "smtp.gmail.com",
          "smtp_port": 587
        },
        "sms": {
          "provider": "twilio",
          "sender_id": "KUMSS"
        },
        "security": {
          "session_timeout": 3600,
          "password_expiry": 90,
          "max_login_attempts": 5
        },
        "features": {
          "online_exam": true,
          "hostel": true,
          "library": true,
          "store": false
        }
      },
      "is_active": true,
      "created_by": {...},
      "updated_by": {...},
      "created_at": "2024-12-04T10:00:00Z",
      "updated_at": "2024-12-04T10:00:00Z"
    }
  ]
}
```

#### 6.2 Create System Settings

```http
POST /api/v1/core/system-settings/
```

**Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "settings": {
    "system": {
      "app_name": "KUMSS ERP",
      "version": "1.0.0",
      "timezone": "America/New_York",
      "date_format": "MM/DD/YYYY",
      "currency": "USD",
      "language": "en"
    },
    "email": {
      "from_address": "noreply@kumss.edu",
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587
    },
    "sms": {
      "provider": "twilio",
      "sender_id": "KUMSS"
    },
    "security": {
      "session_timeout": 3600,
      "password_expiry": 90,
      "max_login_attempts": 5
    },
    "features": {
      "online_exam": true,
      "hostel": true,
      "library": true,
      "store": false
    }
  },
  "is_active": true
}
```

**Validation Rules:**
- Settings JSON must contain all required keys: `system`, `email`, `sms`, `security`, `features`

**Response (201 Created):**
```json
{
  "id": 1,
  "tenant_id": "tenant_001",
  "settings": {...},
  "is_active": true,
  ...
}
```

#### 6.3 Update System Settings

```http
PUT /api/v1/core/system-settings/{id}/
PATCH /api/v1/core/system-settings/{id}/
```

**Note:** DELETE is not allowed for system settings

---

### 7. Notification Settings API

Base path: `/api/v1/core/notification-settings/`

#### 7.1 List Notification Settings

```http
GET /api/v1/core/notification-settings/
```

**Query Parameters:**
- `college` (integer) - Filter by college ID
- `is_active` (boolean) - Filter active settings

**Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": "tenant_001",
      "college": 1,
      "college_name": "MIT",
      "sms_enabled": true,
      "sms_gateway": "twilio",
      "sms_sender_id": "KUMSS",
      "email_enabled": true,
      "email_gateway": "sendgrid",
      "email_from": "noreply@kumss.edu",
      "whatsapp_enabled": false,
      "whatsapp_number": null,
      "attendance_notif": true,
      "fee_reminder": true,
      "fee_days": "7,3,1",
      "notif_settings": {
        "channels": {
          "sms": {
            "attendance_absent": true,
            "fee_due": true,
            "exam_schedule": true
          },
          "email": {
            "attendance_absent": false,
            "fee_due": true,
            "exam_schedule": true
          }
        },
        "schedules": {
          "fee_reminder_time": "09:00",
          "weekly_report_day": "monday"
        }
      },
      "is_active": true,
      "created_by": {...},
      "updated_by": {...},
      "created_at": "2024-12-04T10:00:00Z",
      "updated_at": "2024-12-04T10:00:00Z"
    }
  ]
}
```

**Note:** API keys (`sms_api_key`, `email_api_key`, `whatsapp_api_key`) are write-only and not returned in responses

#### 7.2 Create Notification Settings

```http
POST /api/v1/core/notification-settings/
```

**Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "college": 1,
  "sms_enabled": true,
  "sms_gateway": "twilio",
  "sms_api_key": "your_encrypted_api_key",
  "sms_sender_id": "KUMSS",
  "email_enabled": true,
  "email_gateway": "sendgrid",
  "email_api_key": "your_encrypted_api_key",
  "email_from": "noreply@kumss.edu",
  "whatsapp_enabled": false,
  "whatsapp_api_key": null,
  "whatsapp_number": null,
  "attendance_notif": true,
  "fee_reminder": true,
  "fee_days": "7,3,1",
  "notif_settings": {
    "channels": {
      "sms": {
        "attendance_absent": true,
        "fee_due": true,
        "exam_schedule": true
      }
    },
    "schedules": {
      "fee_reminder_time": "09:00"
    }
  },
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "tenant_id": "tenant_001",
  "college": 1,
  "college_name": "MIT",
  "sms_enabled": true,
  ...
}
```

#### 7.3 Update Notification Settings

```http
PUT /api/v1/core/notification-settings/{id}/
PATCH /api/v1/core/notification-settings/{id}/
```

**Note:** DELETE is not allowed for notification settings

---

### 8. Activity Logs API (Read-Only)

Base path: `/api/v1/core/activity-logs/`

#### 8.1 List Activity Logs

```http
GET /api/v1/core/activity-logs/
```

**Query Parameters:**
- `user` (integer) - Filter by user ID
- `college` (integer) - Filter by college ID
- `action` (string) - Filter by action type
  - Options: `create`, `read`, `update`, `delete`, `login`, `logout`, `download`, `upload`, `export`, `import`
- `model_name` (string) - Filter by model name
- `search` (string) - Search in description, object_id, username
- `ordering` (string) - Sort by `timestamp` (default: `-timestamp`)

**Response (200 OK):**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/core/activity-logs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "tenant_id": "tenant_001",
      "user": 1,
      "user_name": "admin",
      "college": 1,
      "college_name": "MIT",
      "action": "create",
      "action_display": "Create",
      "model_name": "College",
      "object_id": "2",
      "description": "Created new college: Harvard University",
      "metadata": {
        "changes": {
          "name": "Harvard University",
          "code": "HARVARD"
        },
        "request_method": "POST",
        "request_path": "/api/v1/core/colleges/"
      },
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
      "timestamp": "2024-12-04T15:30:00Z"
    }
  ]
}
```

#### 8.2 Get Activity Log Details

```http
GET /api/v1/core/activity-logs/{id}/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "tenant_id": "tenant_001",
  "user": 1,
  "user_name": "admin",
  "college": 1,
  "college_name": "MIT",
  "action": "create",
  "action_display": "Create",
  "model_name": "College",
  "object_id": "2",
  "description": "Created new college: Harvard University",
  "metadata": {...},
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2024-12-04T15:30:00Z"
}
```

**Note:** Activity logs are read-only. No CREATE, UPDATE, or DELETE operations allowed.

---

## 🔧 Frontend Integration Examples

### React/JavaScript Examples

#### 1. Axios Setup with Tenant Header

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1/core',
  withCredentials: true,
  headers: {
    'X-Tenant-ID': localStorage.getItem('tenantId') || 'tenant_001',
    'Content-Type': 'application/json',
  }
});

// Add CSRF token interceptor
api.interceptors.request.use(config => {
  const csrfToken = getCookie('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default api;
```

#### 2. Fetch Colleges with Filters

```javascript
import api from './api';

async function fetchColleges(filters = {}) {
  try {
    const params = new URLSearchParams({
      page: filters.page || 1,
      page_size: filters.pageSize || 20,
      ...(filters.isActive !== undefined && { is_active: filters.isActive }),
      ...(filters.search && { search: filters.search }),
      ...(filters.ordering && { ordering: filters.ordering }),
    });

    const response = await api.get(`/colleges/?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching colleges:', error);
    throw error;
  }
}

// Usage
fetchColleges({
  page: 1,
  pageSize: 10,
  isActive: true,
  search: 'MIT',
  ordering: 'name'
}).then(data => {
  console.log('Colleges:', data.results);
  console.log('Total count:', data.count);
});
```

#### 3. Create New College

```javascript
async function createCollege(collegeData) {
  try {
    const response = await api.post('/colleges/', collegeData);
    return response.data;
  } catch (error) {
    if (error.response) {
      // Validation errors
      console.error('Validation errors:', error.response.data);
    }
    throw error;
  }
}

// Usage
const newCollege = {
  tenant_id: 'tenant_001',
  code: 'STANFORD',
  name: 'Stanford University',
  short_name: 'Stanford',
  email: 'info@stanford.edu',
  phone: '+1-650-723-2300',
  address_line1: '450 Serra Mall',
  city: 'Stanford',
  state: 'California',
  pincode: '94305',
  country: 'USA',
  primary_color: '#8C1515',
  secondary_color: '#FFFFFF',
  settings: {
    academic: {
      attendance_mandatory_percentage: 75,
      max_absent_days: 20,
      grading_system: 'GPA'
    },
    fees: {
      late_fee_percentage: 5,
      installment_allowed: true,
      discount_allowed: false
    },
    notifications: {
      send_birthday_wishes: true,
      send_result_alerts: true
    },
    theme: {
      logo_url: '',
      favicon_url: '',
      primary_font: 'Arial'
    }
  },
  is_main: false,
  display_order: 3,
  is_active: true
};

createCollege(newCollege)
  .then(college => console.log('Created:', college))
  .catch(error => console.error('Error:', error));
```

#### 4. Update College

```javascript
async function updateCollege(id, updates) {
  try {
    const response = await api.patch(`/colleges/${id}/`, updates);
    return response.data;
  } catch (error) {
    console.error('Error updating college:', error);
    throw error;
  }
}

// Usage
updateCollege(1, {
  email: 'newemail@mit.edu',
  phone: '+1-617-253-2000'
}).then(college => console.log('Updated:', college));
```

#### 5. Get Current Academic Year

```javascript
async function getCurrentAcademicYear() {
  try {
    const response = await api.get('/academic-years/current/');
    return response.data;
  } catch (error) {
    if (error.response && error.response.status === 404) {
      console.log('No current academic year found');
      return null;
    }
    throw error;
  }
}

// Usage
getCurrentAcademicYear().then(year => {
  if (year) {
    console.log('Current year:', year.year);
    console.log('Start date:', year.start_date);
  }
});
```

#### 6. Create Holiday with File Upload

```javascript
async function createHoliday(holidayData) {
  try {
    const response = await api.post('/holidays/', holidayData);
    return response.data;
  } catch (error) {
    console.error('Error creating holiday:', error);
    throw error;
  }
}

// Usage
const holiday = {
  tenant_id: 'tenant_001',
  college: 1,
  name: 'Thanksgiving',
  date: '2025-11-27',
  holiday_type: 'national',
  description: 'Thanksgiving Day',
  is_active: true
};

createHoliday(holiday).then(result => console.log('Created:', result));
```

#### 7. Fetch Activity Logs with Filters

```javascript
async function fetchActivityLogs(filters = {}) {
  try {
    const params = new URLSearchParams({
      page: filters.page || 1,
      ...(filters.user && { user: filters.user }),
      ...(filters.college && { college: filters.college }),
      ...(filters.action && { action: filters.action }),
      ordering: filters.ordering || '-timestamp'
    });

    const response = await api.get(`/activity-logs/?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching logs:', error);
    throw error;
  }
}

// Usage
fetchActivityLogs({
  action: 'create',
  college: 1,
  page: 1
}).then(data => {
  console.log('Activity logs:', data.results);
});
```

#### 8. Bulk Delete Colleges

```javascript
async function bulkDeleteColleges(ids) {
  try {
    const response = await api.post('/colleges/bulk_delete/', { ids });
    return response.data;
  } catch (error) {
    console.error('Error bulk deleting:', error);
    throw error;
  }
}

// Usage
bulkDeleteColleges([1, 2, 3]).then(result => {
  console.log(result.message);
  console.log('Deleted IDs:', result.deleted_ids);
});
```

---

## ⚠️ Error Handling

### Common HTTP Status Codes

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Deletion successful
- **400 Bad Request** - Validation error
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

### Error Response Format

```json
{
  "field_name": [
    "Error message 1",
    "Error message 2"
  ],
  "non_field_errors": [
    "General error message"
  ]
}
```

### Frontend Error Handling Example

```javascript
async function handleApiCall(apiFunction) {
  try {
    const result = await apiFunction();
    return { success: true, data: result };
  } catch (error) {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const errors = error.response.data;

      switch (status) {
        case 400:
          return { success: false, errors, message: 'Validation failed' };
        case 401:
          // Redirect to login
          window.location.href = '/login';
          return { success: false, message: 'Please login' };
        case 403:
          return { success: false, message: 'Permission denied' };
        case 404:
          return { success: false, message: 'Resource not found' };
        default:
          return { success: false, message: 'An error occurred' };
      }
    } else if (error.request) {
      // Request made but no response
      return { success: false, message: 'Network error' };
    } else {
      // Something else happened
      return { success: false, message: error.message };
    }
  }
}

// Usage
const result = await handleApiCall(() => createCollege(collegeData));
if (result.success) {
  console.log('Success:', result.data);
} else {
  console.error('Error:', result.message, result.errors);
}
```

---

## 🎨 UI Component Examples

### College Selector Component (React)

```jsx
import React, { useState, useEffect } from 'react';
import api from './api';

function CollegeSelector({ onSelect }) {
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchActiveColleges();
  }, []);

  async function fetchActiveColleges() {
    try {
      const response = await api.get('/colleges/active/');
      setColleges(response.data);
    } catch (error) {
      console.error('Error fetching colleges:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Loading...</div>;

  return (
    <select onChange={(e) => onSelect(e.target.value)}>
      <option value="">Select College</option>
      {colleges.map(college => (
        <option key={college.id} value={college.id}>
          {college.name} ({college.code})
        </option>
      ))}
    </select>
  );
}

export default CollegeSelector;
```

### Holiday Calendar Component

```jsx
import React, { useState, useEffect } from 'react';
import api from './api';

function HolidayCalendar({ collegeId }) {
  const [holidays, setHolidays] = useState([]);

  useEffect(() => {
    if (collegeId) {
      fetchHolidays();
    }
  }, [collegeId]);

  async function fetchHolidays() {
    try {
      const response = await api.get(`/holidays/?college=${collegeId}&ordering=date`);
      setHolidays(response.data.results);
    } catch (error) {
      console.error('Error fetching holidays:', error);
    }
  }

  return (
    <div className="holiday-calendar">
      <h3>Holidays</h3>
      {holidays.length === 0 ? (
        <p>No holidays found</p>
      ) : (
        <ul>
          {holidays.map(holiday => (
            <li key={holiday.id}>
              <strong>{holiday.name}</strong> - {holiday.date}
              <span className={`badge ${holiday.holiday_type}`}>
                {holiday.holiday_type_display}
              </span>
              {holiday.description && <p>{holiday.description}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default HolidayCalendar;
```

---

## 📱 Mobile App Integration (React Native)

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://api.kumss.edu/api/v1/core';

async function apiCall(endpoint, options = {}) {
  const tenantId = await AsyncStorage.getItem('tenantId');
  const sessionId = await AsyncStorage.getItem('sessionId');

  const headers = {
    'X-Tenant-ID': tenantId,
    'Content-Type': 'application/json',
    'Cookie': `sessionid=${sessionId}`,
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(JSON.stringify(error));
  }

  return response.json();
}

// Usage
async function getColleges() {
  return apiCall('/colleges/?is_active=true');
}

async function createAcademicYear(yearData) {
  return apiCall('/academic-years/', {
    method: 'POST',
    body: JSON.stringify(yearData),
  });
}
```

---

## 📊 Testing & Debugging

### Using Browser Console

```javascript
// Test API connection
fetch('/api/v1/core/colleges/', {
  headers: {
    'X-Tenant-ID': 'tenant_001'
  },
  credentials: 'include'
})
.then(r => r.json())
.then(data => console.log(data));

// Test with authentication
const csrfToken = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrftoken='))
  ?.split('=')[1];

fetch('/api/v1/core/colleges/', {
  method: 'POST',
  headers: {
    'X-Tenant-ID': 'tenant_001',
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  credentials: 'include',
  body: JSON.stringify({
    tenant_id: 'tenant_001',
    code: 'TEST',
    name: 'Test College',
    // ... other fields
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 📝 Notes for Frontend Developers

1. **Always include X-Tenant-ID header** in all requests
2. **CSRF Token required** for POST, PUT, PATCH, DELETE requests
3. **Session authentication** - Use cookies for authentication
4. **Pagination** - All list endpoints return paginated results
5. **Filtering** - Use query parameters for filtering
6. **Soft Delete** - DELETE operations set `is_active=false`
7. **Automatic Signals** - College creation triggers automatic weekend and notification settings creation
8. **Read-Only Logs** - Activity logs cannot be created/modified via API
9. **Validation** - Server-side validation returns 400 with field-specific errors
10. **Date Format** - Use ISO 8601 format (YYYY-MM-DD) for dates

---

## 🔗 Additional Resources

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin Panel**: http://localhost:8000/admin/

For any questions or issues, contact the backend development team.
