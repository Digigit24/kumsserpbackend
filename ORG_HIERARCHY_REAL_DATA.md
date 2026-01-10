# Organizational Hierarchy - Real Data Approach

## Overview
The organizational hierarchy system now **automatically displays roles based on actual users** in your database. No seeding or manual role creation needed!

## How It Works

### Data Source
The system reads directly from the `User` table and groups users by their `user_type` field:

```sql
SELECT user_type, COUNT(*)
FROM users
WHERE college_id = ? AND is_active = TRUE
GROUP BY user_type
```

### Automatic Role Creation
For each `user_type` found, the system:
1. **Fetches the count** of users with that type
2. **Creates a virtual role node** with a friendly display name
3. **Shows the count** (e.g., "Student (150)", "Teacher (5)")

### Supported User Types
The system recognizes these common user types:

| user_type      | Display Name   | Hierarchy Level |
|---------------|----------------|-----------------|
| student       | Student        | 10              |
| teacher       | Teacher        | 5               |
| hod           | HOD            | 4               |
| principal     | Principal      | 2               |
| staff         | Staff          | 7               |
| store_manager | Store Manager  | 6               |
| librarian     | Librarian      | 7               |
| accountant    | Accountant     | 6               |
| lab_assistant | Lab Assistant  | 8               |
| clerk         | Clerk          | 8               |
| college_admin | College Admin  | 3               |

**Unknown types** are automatically formatted (e.g., `my_custom_role` → "My Custom Role")

## API Endpoints

### 1. Tree Structure
```
GET /api/core/organization/nodes/tree/
Headers: X-College-Id: 3
```

Returns hierarchical tree with all roles and their counts.

### 2. Roles Summary
```
GET /api/core/organization/nodes/roles_summary/
Headers: X-College-Id: 3
```

Returns flat list of roles with counts per college.

**Example Response:**
```json
{
  "KUMSS Engineering College": {
    "college_id": 3,
    "college_name": "KUMSS Engineering College",
    "total_roles": 4,
    "roles": [
      {
        "role_name": "Principal",
        "role_code": "principal",
        "count": 1,
        "level": 2
      },
      {
        "role_name": "Teacher",
        "role_code": "teacher",
        "count": 5,
        "level": 5
      },
      {
        "role_name": "Student",
        "role_code": "student",
        "count": 150,
        "level": 10
      }
    ]
  }
}
```

## What Changed

### Before (Role-Driven)
- Required roles to be defined in `DynamicRole` or `AccountRole` tables
- Empty roles wouldn't show unless explicitly created
- Students wouldn't appear if no "Student" role existed

### After (User-Driven)
- ✅ Reads actual users from database
- ✅ Automatically creates role nodes
- ✅ Shows real counts from `user_type` field
- ✅ No seeding required!

## Fallback Behavior

The system has a priority order:

1. **AccountRole** - If defined, uses these roles with parent/child relationships
2. **DynamicRole** - If defined, uses these with hierarchy levels
3. **Auto-Generated** - Falls back to user_type from database

This means:
- Colleges with predefined roles use the role structure
- Colleges without predefined roles automatically show user-based roles
- **Both approaches work simultaneously**

## Performance

- Uses efficient aggregation queries
- Cached for 5 minutes
- Single query per college for user counts
- No N+1 query issues

## Privacy

As requested:
- ❌ No user names displayed
- ❌ No personal information
- ✅ Only role names and counts
- ✅ Aggregated statistics only

## Testing

To verify it works with your data:

1. **Check your users:**
   ```sql
   SELECT college_id, user_type, COUNT(*)
   FROM users
   WHERE is_active = TRUE
   GROUP BY college_id, user_type;
   ```

2. **Call the API:**
   ```bash
   curl -H "X-College-Id: 3" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/core/organization/nodes/roles_summary/
   ```

3. **Verify counts match** your database query

## Notes

- Cache is cleared on node create/update
- Super admin users excluded from counts
- Only active users counted (`is_active=True`)
- College filtering via `X-College-Id` header
