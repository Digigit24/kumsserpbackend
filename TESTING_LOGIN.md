# Testing the Enhanced Login Response

## The Changes ARE Applied!

All user details are now included in the login API response. Here's how to verify:

## Method 1: Using the Test Script

1. **Start your Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Run the test script:**
   ```bash
   python test_login_response.py
   ```

3. **Update credentials in the script if needed:**
   Edit `test_login_response.py` and change:
   ```python
   TEST_CREDENTIALS = {
       "username": "your_username",
       "password": "your_password"
   }
   ```

## Method 2: Using Postman/Thunder Client/Insomnia

**Endpoint:** `POST http://localhost:8000/api/v1/auth/login/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Expected Response (200 OK):**
```json
{
  "key": "your_auth_token_here",
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
    "avatar": null,
    "college": 1,
    "college_name": "Your College",
    "user_type": "admin",
    "user_type_display": "Admin",
    "is_active": true,
    "is_staff": true,
    "is_verified": true,
    "last_login": "2025-12-25T12:00:00Z",
    "last_login_ip": "127.0.0.1",
    "date_joined": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2025-12-25T12:00:00Z"
  },
  "college_id": 1,
  "tenant_ids": [1],
  "accessible_colleges": [
    {
      "id": 1,
      "code": "ABC",
      "name": "ABC College",
      "short_name": "ABC"
    }
  ],
  "user_roles": [
    {
      "id": 1,
      "role_id": 5,
      "role_name": "Admin",
      "role_code": "ADMIN",
      "college_id": 1,
      "college_name": "ABC",
      "assigned_at": "2024-01-01T00:00:00Z",
      "expires_at": null,
      "is_expired": false
    }
  ],
  "user_permissions": [
    "*"
  ],
  "user_profile": {
    "id": 1,
    "department_id": 1,
    "department_name": "Administration",
    "address_line1": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "country": "India",
    ...
  }
}
```

## Method 3: Using cURL

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' \
  | python -m json.tool
```

## Method 4: Frontend JavaScript/React

```javascript
const loginUser = async (username, password) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  });

  const data = await response.json();

  console.log('=== LOGIN RESPONSE ===');
  console.log('Full Response:', data);
  console.log('Auth Token:', data.key);
  console.log('User Object:', data.user);
  console.log('User Roles:', data.user_roles);
  console.log('User Permissions:', data.user_permissions);
  console.log('User Profile:', data.user_profile);

  return data;
};
```

## What You'll See in Frontend Response Tab

In your browser's DevTools Network tab or API testing tool:

1. **Status:** 200 OK
2. **Response Body:** Complete JSON with ALL fields shown above
3. **User Object:** All user details with keys visible
4. **Additional Fields:** roles, permissions, profile, colleges

## Troubleshooting

### If you don't see all fields:

1. **Restart Django Server:**
   ```bash
   # Stop the server (Ctrl+C)
   python manage.py runserver
   ```

2. **Check Python is using the correct code:**
   ```bash
   git log -1  # Should show: "Enhance login response with comprehensive user details"
   ```

3. **Verify serializer is configured:**
   ```bash
   grep -A 2 "REST_AUTH_SERIALIZERS" kumss_erp/settings/base.py
   ```
   Should show:
   ```python
   REST_AUTH_SERIALIZERS = {
       'TOKEN_SERIALIZER': 'apps.accounts.serializers.TokenWithUserSerializer',
   }
   ```

### If user_profile is null:

This is normal if the user doesn't have a profile created yet. Create one via:
```python
python manage.py shell
from apps.accounts.models import User, UserProfile
user = User.objects.get(username='your_username')
UserProfile.objects.create(user=user, college=user.college)
```

## Server Console Logs

Additionally, when a user logs in, the **server console** will also display:
```
================================================================================
LOGIN SUCCESSFUL
================================================================================
Complete Response Data:
{
  "key": "...",
  "message": "Welcome back, John Doe! Login successful.",
  "user": {...},
  ...
}
--------------------------------------------------------------------------------
USER DETAILS:
--------------------------------------------------------------------------------
  id: ...
  username: johndoe
  email: john.doe@example.com
  ...
```

This helps with debugging during development.
