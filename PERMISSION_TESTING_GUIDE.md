# KUMSS Permission System - Testing Guide

This guide will help you verify the permission system is working correctly and ensure the frontend team has all the data they need.

## Step 1: Setup Database Tables

First, create and apply the migrations:

```bash
# Create migrations for the new Permission and TeamMembership models
python manage.py makemigrations accounts
python manage.py makemigrations core

# Apply all migrations
python manage.py migrate
```

## Step 2: Seed Default Permissions

```bash
# This will create default permissions for all roles in all active colleges
python manage.py seed_permissions
```

Expected output:
```
Seeding permissions for 5 roles in 1 colleges...
✓ Created permission for College: Main Campus, Role: admin
✓ Created permission for College: Main Campus, Role: hod
✓ Created permission for College: Main Campus, Role: teacher
✓ Created permission for College: Main Campus, Role: student
✓ Created permission for College: Main Campus, Role: staff
Successfully seeded 5 permissions.
```

## Step 3: Verify Permission Data in Database

```bash
# Check if permissions were created
python manage.py shell
```

Then in the shell:
```python
from apps.core.models import Permission
from apps.accounts.models import User

# Check all permissions
permissions = Permission.objects.all()
for p in permissions:
    print(f"College: {p.college.name}, Role: {p.role}")

# Check a specific role's permissions
student_perm = Permission.objects.filter(role='student').first()
print(student_perm.permissions_json)
```

## Step 4: Test Login Endpoint

### 4.1 Create Test Users

```bash
# Create a student user
python manage.py shell
```

```python
from apps.accounts.models import User
from apps.core.models import College

college = College.objects.first()

# Create student
student = User.objects.create_user(
    username='test_student',
    email='student@test.com',
    password='test123',
    user_type='student',
    college=college,
    first_name='Test',
    last_name='Student'
)

# Create teacher
teacher = User.objects.create_user(
    username='test_teacher',
    email='teacher@test.com',
    password='test123',
    user_type='teacher',
    college=college,
    first_name='Test',
    last_name='Teacher'
)

# Create admin
admin = User.objects.create_user(
    username='test_admin',
    email='admin@test.com',
    password='test123',
    user_type='admin',
    college=college,
    first_name='Test',
    last_name='Admin'
)

print("Test users created successfully!")
```

### 4.2 Test Login Response

Use Postman, curl, or any HTTP client to test the login endpoint.

**Request:**
```http
POST /api/accounts/login/
Content-Type: application/json
X-College-ID: 1

{
    "username": "test_student",
    "password": "test123"
}
```

**Expected Response Structure:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": "uuid-here",
        "username": "test_student",
        "email": "student@test.com",
        "first_name": "Test",
        "last_name": "Student",
        "user_type": "student",
        "is_active": true,
        "college_id": 1,
        "college_name": "Main Campus",
        "department_id": null,
        "department_name": null,
        "user_roles": [
            {
                "role_name": "Student",
                "role_code": "student",
                "is_primary": true,
                "description": "Student user",
                "permissions_count": 17
            }
        ],
        "user_permissions": {
            "attendance": {
                "create": {
                    "enabled": false,
                    "scope": "none"
                },
                "read": {
                    "enabled": true,
                    "scope": "mine"
                },
                "update": {
                    "enabled": false,
                    "scope": "none"
                },
                "delete": {
                    "enabled": false,
                    "scope": "none"
                },
                "export": {
                    "enabled": false,
                    "scope": "none"
                }
            },
            "students": {
                "create": {
                    "enabled": false,
                    "scope": "none"
                },
                "read": {
                    "enabled": true,
                    "scope": "mine"
                },
                "update": {
                    "enabled": true,
                    "scope": "mine"
                },
                "delete": {
                    "enabled": false,
                    "scope": "none"
                }
            },
            "fees": {
                "read": {
                    "enabled": true,
                    "scope": "mine"
                }
            },
            "examinations": {
                "read": {
                    "enabled": true,
                    "scope": "mine"
                }
            },
            "library": {
                "read": {
                    "enabled": true,
                    "scope": "mine"
                },
                "issue_book": {
                    "enabled": true,
                    "scope": "mine"
                }
            }
        },
        "user_profile": null
    }
}
```

## Step 5: Frontend Integration Testing

### 5.1 Permission Helper Functions

Provide these helper functions to your frontend team:

```javascript
// Store the user permissions from login response
const userPermissions = loginResponse.user.user_permissions;

/**
 * Check if user has permission for a specific action on a resource
 * @param {string} resource - Resource name (e.g., 'attendance', 'students')
 * @param {string} action - Action name (e.g., 'create', 'read', 'update', 'delete')
 * @returns {boolean} - True if permission is enabled
 */
function hasPermission(resource, action) {
    return userPermissions?.[resource]?.[action]?.enabled || false;
}

/**
 * Get the scope for a specific resource-action
 * @param {string} resource - Resource name
 * @param {string} action - Action name
 * @returns {string} - Scope value ('none', 'mine', 'team', 'department', 'all')
 */
function getPermissionScope(resource, action) {
    return userPermissions?.[resource]?.[action]?.scope || 'none';
}

/**
 * Check if user can perform any action on a resource
 * @param {string} resource - Resource name
 * @returns {boolean} - True if any action is enabled
 */
function hasAnyPermission(resource) {
    const resourcePerms = userPermissions?.[resource];
    if (!resourcePerms) return false;

    return Object.values(resourcePerms).some(perm => perm.enabled);
}

// Usage Examples:

// 1. Conditional rendering of buttons
if (hasPermission('students', 'create')) {
    // Show "Add Student" button
}

if (hasPermission('students', 'update')) {
    // Show "Edit" button
}

if (hasPermission('students', 'delete')) {
    // Show "Delete" button
}

// 2. Conditional navigation/routes
if (hasAnyPermission('attendance')) {
    // Show attendance menu item
}

// 3. Scope-based filtering
const attendanceScope = getPermissionScope('attendance', 'read');
if (attendanceScope === 'mine') {
    // Fetch only my attendance
    fetchAttendance({ student_id: currentUserId });
} else if (attendanceScope === 'all') {
    // Fetch all attendance
    fetchAttendance();
}
```

### 5.2 UI Component Examples

**Example 1: Conditional Button Rendering (React)**
```jsx
function StudentActions({ student }) {
    const permissions = usePermissions(); // Custom hook that gets permissions

    return (
        <div className="actions">
            {permissions.has('students', 'read') && (
                <button onClick={() => viewStudent(student)}>View</button>
            )}

            {permissions.has('students', 'update') && (
                <button onClick={() => editStudent(student)}>Edit</button>
            )}

            {permissions.has('students', 'delete') && (
                <button onClick={() => deleteStudent(student)}>Delete</button>
            )}
        </div>
    );
}
```

**Example 2: Conditional Menu Items (React)**
```jsx
function Sidebar() {
    const permissions = usePermissions();

    return (
        <nav>
            {permissions.hasAny('students') && (
                <NavItem to="/students" icon="users">Students</NavItem>
            )}

            {permissions.hasAny('attendance') && (
                <NavItem to="/attendance" icon="check">Attendance</NavItem>
            )}

            {permissions.hasAny('fees') && (
                <NavItem to="/fees" icon="dollar">Fees</NavItem>
            )}

            {permissions.hasAny('examinations') && (
                <NavItem to="/exams" icon="file">Examinations</NavItem>
            )}
        </nav>
    );
}
```

**Example 3: Form Field Permissions**
```jsx
function StudentForm({ student, mode }) {
    const permissions = usePermissions();
    const canEdit = permissions.has('students', 'update');
    const isViewOnly = mode === 'view' || !canEdit;

    return (
        <form>
            <input
                name="firstName"
                value={student.firstName}
                disabled={isViewOnly}
            />

            <input
                name="email"
                value={student.email}
                disabled={isViewOnly}
            />

            {canEdit && (
                <button type="submit">Save Changes</button>
            )}
        </form>
    );
}
```

## Step 6: Test Different User Roles

### Test Matrix

| Role | Resource | Actions | Expected Scope |
|------|----------|---------|----------------|
| **Student** | attendance | read | mine |
| **Student** | students | read, update | mine |
| **Student** | fees | read | mine |
| **Student** | examinations | read | mine |
| **Teacher** | attendance | create, read, update, delete | team |
| **Teacher** | students | read, update | team |
| **Teacher** | examinations | create, read, update | team |
| **Admin** | ALL | ALL | all |
| **HOD** | attendance | ALL | department |
| **HOD** | students | ALL | department |
| **HOD** | teachers | ALL | department |

### Testing Checklist

For each user role, verify:

- [ ] Login response includes `user_permissions` object
- [ ] Login response includes `user_roles` array
- [ ] `user_permissions` has correct resources for the role
- [ ] Each action has both `enabled` (boolean) and `scope` (string) fields
- [ ] Student can only see "mine" scope permissions
- [ ] Teacher can see "team" scope permissions
- [ ] Admin can see "all" scope permissions
- [ ] Disabled permissions have `enabled: false`
- [ ] Frontend buttons/menus hide correctly based on permissions

## Step 7: API Endpoint Testing

### Get My Permissions
```http
GET /api/core/permissions/my-permissions/
Authorization: Bearer <access_token>
X-College-ID: 1
```

**Response:**
```json
{
    "user_id": "uuid",
    "username": "test_student",
    "is_superadmin": false,
    "college_id": "1",
    "role": "student",
    "permissions": {
        "attendance": {
            "read": {"enabled": true, "scope": "mine"}
        }
        // ... more permissions
    }
}
```

### Get Permission Schema
```http
GET /api/core/permissions/schema/
Authorization: Bearer <access_token>
X-College-ID: 1
```

**Response:**
```json
{
    "resources": {
        "attendance": {
            "actions": ["create", "read", "update", "delete", "export"],
            "description": "Student attendance management"
        },
        "students": {
            "actions": ["create", "read", "update", "delete", "import", "export"],
            "description": "Student information management"
        }
        // ... more resources
    },
    "scopes": ["none", "mine", "team", "department", "all"]
}
```

### List All Permissions (Admin Only)
```http
GET /api/core/permissions/
Authorization: Bearer <admin_access_token>
X-College-ID: 1
```

### Update Role Permissions (Admin Only)
```http
PATCH /api/core/permissions/{id}/
Authorization: Bearer <admin_access_token>
X-College-ID: 1
Content-Type: application/json

{
    "permissions_json": {
        "attendance": {
            "create": {"enabled": true, "scope": "team"},
            "read": {"enabled": true, "scope": "all"}
        }
    }
}
```

## Step 8: Common Issues & Troubleshooting

### Issue 1: Empty Permissions in Login Response

**Problem:** `user_permissions: {}`

**Solution:**
1. Verify permissions are seeded: `python manage.py seed_permissions`
2. Check user has a `user_type` set
3. Verify college_id is present in user model
4. Check Permission model has entry for the user's role

### Issue 2: All Permissions Show as Disabled

**Problem:** All actions have `enabled: false`

**Solution:**
1. Check the Permission record in database
2. Verify `permissions_json` field is not empty
3. Run seed command to reset to defaults
4. Check for JSON validation errors in serializer

### Issue 3: Frontend Can't Access Nested Permissions

**Problem:** `Cannot read property 'enabled' of undefined`

**Solution:**
```javascript
// Always use safe access
const hasPermission = userPermissions?.attendance?.read?.enabled || false;

// Or use the helper function
function hasPermission(resource, action) {
    return userPermissions?.[resource]?.[action]?.enabled || false;
}
```

### Issue 4: Permissions Not Updating After Role Change

**Problem:** User's permissions don't change after updating their user_type

**Solution:**
1. User must logout and login again to get fresh token
2. Permissions are embedded in login response, not in JWT token
3. Frontend should clear cached permissions on logout
4. Consider implementing a "refresh permissions" API endpoint if needed

## Step 9: Performance Considerations

### Caching Recommendations

**Backend:**
- Cache Permission objects per college/role combination
- Use Django's select_related for college and user queries
- Consider Redis for permission lookups if scaling issues occur

**Frontend:**
- Store permissions in global state (Redux, Zustand, Context)
- Don't make API calls to check permissions on every component
- Use the login response data throughout the session
- Clear permissions on logout

### Best Practices

1. **Don't send permissions in every API response** - Only in login response
2. **Validate permissions on backend** - Frontend checks are for UI only
3. **Use permission mixins in viewsets** - Let backend enforce access control
4. **Log permission denials** - Track when users try unauthorized actions
5. **Provide clear error messages** - Tell users why they can't perform actions

## Step 10: Documentation for Frontend Team

Provide your frontend team with:

1. **This testing guide** - So they understand the permission structure
2. **Sample login responses** - For each user role
3. **Helper functions** - JavaScript utilities for checking permissions
4. **Component examples** - How to implement conditional rendering
5. **API endpoint list** - All permission-related endpoints
6. **Error scenarios** - What to do when permissions are missing
7. **Logout handling** - How to clear permissions from state

## Quick Verification Checklist

Before handing off to frontend team:

- [ ] Migrations applied successfully
- [ ] Default permissions seeded for all roles
- [ ] Test user accounts created (student, teacher, admin)
- [ ] Login endpoint returns `user_permissions` object
- [ ] Login endpoint returns `user_roles` array
- [ ] Student user shows limited permissions
- [ ] Teacher user shows team-level permissions
- [ ] Admin user shows all permissions
- [ ] All resources have proper action definitions
- [ ] All actions have both `enabled` and `scope` fields
- [ ] Permission schema endpoint works
- [ ] My permissions endpoint works
- [ ] Frontend helper functions provided
- [ ] Testing guide shared with team

## Support & Questions

If frontend team encounters issues:

1. First check this testing guide
2. Verify backend setup is complete (all checkboxes above)
3. Test with Postman/curl to isolate if issue is backend or frontend
4. Check browser console for permission-related errors
5. Verify X-College-ID header is being sent
6. Ensure user is authenticated (valid access token)

---

**Last Updated:** 2025-12-29
**Version:** 1.0
**Contact:** Backend Team
