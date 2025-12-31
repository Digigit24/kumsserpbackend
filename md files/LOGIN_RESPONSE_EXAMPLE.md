# Enhanced Login Response Documentation

## Overview
When a user logs in (admin, superuser, or regular user), the API now returns comprehensive user details including all user information, roles, permissions, and profile data.

## Endpoint
```
POST /api/v1/auth/login/
```

## Request Body
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

## Enhanced Response Structure

The login endpoint now returns the following comprehensive data:

```json
{
  "key": "authentication_token_here",
  "message": "Welcome back, John Doe! Login successful.",
  "user": {
    "id": "uuid-here",
    "username": "johndoe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "middle_name": "",
    "full_name": "John Doe",
    "gender": "male",
    "gender_display": "Male",
    "date_of_birth": "1990-01-15",
    "avatar": "/media/avatars/john.jpg",
    "college": 1,
    "college_name": "ABC College",
    "user_type": "teacher",
    "user_type_display": "Teacher",
    "is_active": true,
    "is_staff": false,
    "is_verified": true,
    "last_login": "2025-12-25T10:30:00Z",
    "last_login_ip": "192.168.1.100",
    "date_joined": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2025-12-25T10:30:00Z"
  },
  "college_id": 1,
  "tenant_ids": [1, 2],
  "accessible_colleges": [
    {
      "id": 1,
      "code": "ABC",
      "name": "ABC College of Engineering",
      "short_name": "ABC College"
    },
    {
      "id": 2,
      "code": "XYZ",
      "name": "XYZ College of Technology",
      "short_name": "XYZ College"
    }
  ],
  "user_roles": [
    {
      "id": 1,
      "role_id": 5,
      "role_name": "Department Head",
      "role_code": "DEPT_HEAD",
      "college_id": 1,
      "college_name": "ABC College",
      "assigned_at": "2024-01-15T00:00:00Z",
      "expires_at": null,
      "is_expired": false
    }
  ],
  "user_permissions": [
    "can_manage_department",
    "can_approve_leaves",
    "can_view_reports"
  ],
  "user_profile": {
    "id": 1,
    "department_id": 3,
    "department_name": "Computer Science",
    "address_line1": "123 Main Street",
    "address_line2": "Apt 4B",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "country": "India",
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_phone": "+1234567891",
    "emergency_contact_relation": "Spouse",
    "blood_group": "O+",
    "nationality": "Indian",
    "religion": "Hindu",
    "caste": "General",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "website_url": "https://johndoe.com",
    "bio": "Experienced professor with 10 years of teaching experience."
  }
}
```

## Console Logging

When a user successfully logs in, the server console will display:

```
================================================================================
LOGIN SUCCESSFUL
================================================================================
Complete Response Data:
{
  "key": "...",
  "message": "Welcome back, John Doe! Login successful.",
  "user": { ... },
  ...
}
--------------------------------------------------------------------------------
USER DETAILS:
--------------------------------------------------------------------------------
  id: uuid-here
  username: johndoe
  email: john.doe@example.com
  phone: +1234567890
  first_name: John
  last_name: Doe
  ...
--------------------------------------------------------------------------------
Authentication Token: auth_token_here
--------------------------------------------------------------------------------
Primary College ID: 1
Accessible Colleges:
  - {'id': 1, 'code': 'ABC', 'name': 'ABC College', ...}
  - {'id': 2, 'code': 'XYZ', 'name': 'XYZ College', ...}
================================================================================
```

## Response Fields Explained

### Core Fields
- **key**: Authentication token for subsequent API requests
- **message**: Personalized welcome message
- **user**: Complete user object with all profile information
- **college_id**: Primary college ID for the user
- **tenant_ids**: List of all college IDs the user has access to

### Additional Fields
- **accessible_colleges**: Detailed information about all colleges the user can access
- **user_roles**: All active roles assigned to the user across different colleges
- **user_permissions**: Aggregated list of permissions from all assigned roles
- **user_profile**: Extended profile information including address, emergency contacts, etc.

## User Types Supported

The enhanced response works for all user types:
- **Superuser**: Returns `["*"]` for permissions (all permissions)
- **Admin**: Returns all assigned permissions
- **Teacher**: Returns teacher-specific roles and permissions
- **Student**: Returns student-specific roles and permissions
- **Staff**: Returns staff-specific roles and permissions

## Notes

1. The response automatically adapts based on user type and assigned roles
2. Superusers without a specific college get `college_id: 0` and access to all colleges
3. User profile is `null` if not created yet
4. Permissions are aggregated from all active, non-expired roles
5. All datetime fields are in ISO 8601 format with UTC timezone
