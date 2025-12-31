# User Profile Setup Guide

This guide explains how to set up user profiles for the login response to include complete user data.

## Changes Made

### 1. Auto-Creation Signal (`apps/accounts/signals.py`)
A signal has been added to automatically create a `UserProfile` when a new `User` is created. This ensures all new users will have a profile.

### 2. Management Command
A management command has been created to create profiles for existing users who don't have them.

## Setup Steps

### Step 1: Create Profiles for Existing Users

Run this command to create profiles for all existing users:

```bash
python manage.py create_user_profiles
```

This will:
- Find all users with a college assigned but no profile
- Create a UserProfile for each of them
- Show a summary of created profiles

### Step 2: Verify Your College ID

Make sure you're sending a **valid numeric college ID** in the `X-College-ID` header when logging in.

**IMPORTANT**: The header value should be a number, not a string like 'a'.

Example of correct headers:
```
X-College-ID: 1
```

NOT:
```
X-College-ID: a
```

### Step 3: Test Login

After running the management command and ensuring correct headers, test your login endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -H "X-College-ID: 1" \
  -d '{"username": "your_username", "password": "your_password"}'
```

You should now receive a response with:
- `user`: Complete user details
- `college_id`: Primary college ID
- `tenant_ids`: Array of accessible college IDs
- `accessible_colleges`: Array of college details
- `user_roles`: Array of assigned roles (empty if no roles assigned)
- `user_permissions`: Array of permissions (empty if no roles)
- `user_profile`: User profile data (null only if user has no college)

## Expected Response Format

```json
{
  "key": "your-auth-token",
  "message": "Welcome back, John Doe! Login successful.",
  "user": {
    "id": "uuid-here",
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "college": 1,
    "college_name": "ABC College",
    ...
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
  "user_roles": [],
  "user_permissions": [],
  "user_profile": {
    "id": 1,
    "department_id": null,
    "department_name": null,
    "address_line1": null,
    ...
  }
}
```

## Assigning User Roles

If you want `user_roles` and `user_permissions` to be populated:

1. Create roles in the admin panel or via API: `/api/v1/accounts/roles/`
2. Assign roles to users: `/api/v1/accounts/user-roles/`

Example role assignment:
```json
{
  "user": "user-uuid",
  "role": 1,
  "college": 1
}
```

## Troubleshooting

### Profile is still null
- Check that the user has a `college` assigned in the database
- Run the management command: `python manage.py create_user_profiles`
- Check server logs for any errors

### user_roles is empty
- This is expected if you haven't assigned any roles to the user
- Assign roles via the admin panel or API

### "X-College-ID: a" error
- Make sure you're sending a numeric college ID (e.g., 1, 2, 3)
- Get valid college IDs from: `/api/v1/core/colleges/`

## Summary

After following these steps, your login endpoint will return comprehensive user data including profile information, roles, and permissions.
