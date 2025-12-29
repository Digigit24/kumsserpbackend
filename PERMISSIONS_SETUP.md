# KUMSS Permission System - Setup Guide

The comprehensive permission system has been successfully implemented! This guide will help you complete the setup.

## ✅ What's Been Implemented

### Phase 1: Database Models
- ✅ Added `is_superadmin` field to User model
- ✅ Created `Permission` model for college-scoped permissions
- ✅ Created `TeamMembership` model for scope filtering
- ✅ Created comprehensive permission registry with all resources

### Phase 2: Permission Engine
- ✅ Updated College Middleware to handle superadmin bypass
- ✅ Created Permission Manager for permission checking
- ✅ Created Scope Resolver for queryset filtering
- ✅ Created DRF Permission Classes (IsSuperAdmin, ResourcePermission)
- ✅ Created Queryset Mixin for scope-based filtering

### Phase 3: API Endpoints
- ✅ Created Permission and TeamMembership serializers
- ✅ Created Permission and TeamMembership ViewSets
- ✅ Registered URLs at `/api/core/permissions/` and `/api/core/team-memberships/`
- ✅ Added custom endpoints:
  - `GET /api/core/permissions/my-permissions/` - Get current user's permissions
  - `GET /api/core/permissions/schema/` - Get permission registry for UI

### Phase 4: ViewSet Integration
- ✅ Updated base ViewSets with optional permission scope filtering
- ✅ Added `resource_name` to core ViewSets (colleges, academic_years, holidays)

### Phase 5: Management Commands
- ✅ Created `create_superadmin` command
- ✅ Created `seed_permissions` command

---

## 🚀 Setup Instructions

### Step 1: Create and Apply Migrations

```bash
# Activate your virtual environment (if you have one)
source venv/bin/activate  # or your virtualenv path

# Create migrations for User model changes
python manage.py makemigrations accounts

# Create migrations for Permission and TeamMembership models
python manage.py makemigrations core

# Apply all migrations
python manage.py migrate
```

### Step 2: Create a Superadmin User

```bash
python manage.py create_superadmin \
  --username=admin \
  --email=admin@example.com \
  --password=YourSecurePassword123 \
  --first-name=Super \
  --last-name=Admin
```

### Step 3: Seed Default Permissions

```bash
# Seed permissions for all active colleges and all roles
python manage.py seed_permissions

# Or seed for a specific college
python manage.py seed_permissions --college=1

# Or seed for a specific role
python manage.py seed_permissions --role=teacher

# To overwrite existing permissions
python manage.py seed_permissions --overwrite
```

### Step 4: Test the System

1. **Test Superadmin Access:**
   ```bash
   # Login as superadmin and test access to all colleges
   # Superadmin does NOT need X-College-ID header
   curl -H "Authorization: Bearer <token>" \
        http://localhost:8000/api/core/colleges/
   ```

2. **Test Permission Endpoints:**
   ```bash
   # Get permission schema
   curl -H "Authorization: Bearer <token>" \
        -H "X-College-ID: 1" \
        http://localhost:8000/api/core/permissions/schema/

   # Get my permissions
   curl -H "Authorization: Bearer <token>" \
        -H "X-College-ID: 1" \
        http://localhost:8000/api/core/permissions/my-permissions/
   ```

3. **Test Scope Filtering:**
   - Login as a teacher and verify you only see students in your team
   - Login as a student and verify you only see your own records

---

## 📝 How to Add Permissions to Other ViewSets

To enable permission-based access control on any ViewSet:

1. **Add `resource_name` to your ViewSet:**

```python
# Example: apps/attendance/views.py
class AttendanceViewSet(CollegeScopedModelViewSet):
    resource_name = 'attendance'  # Add this line
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    # ... rest of your ViewSet
```

2. **Optionally add `action_permission_map` for custom actions:**

```python
class AttendanceViewSet(CollegeScopedModelViewSet):
    resource_name = 'attendance'

    action_permission_map = {
        'list': 'read',
        'retrieve': 'read',
        'create': 'create',
        'update': 'update',
        'destroy': 'delete',
        'export': 'export',  # Custom action
    }

    @action(detail=False, methods=['get'])
    def export(self, request):
        # Permission check is automatic
        # ...
```

3. **The system automatically:**
   - ✅ Checks if user has permission for the action
   - ✅ Applies scope filtering (mine/team/department/all)
   - ✅ Handles superadmin bypass
   - ✅ Maintains college isolation

---

## 🎯 Permission Registry

The following resources are available in the permission registry:

- `attendance` - Student attendance management
- `students` - Student records management
- `fees` - Fee management
- `examinations` - Examination and results management
- `library` - Library management
- `hr` - Human resources management
- `hostel` - Hostel management
- `academic` - Academic program management
- `accounting` - Accounting and finance management
- `communication` - Communication and messaging
- `teachers` - Teacher records management
- `online_exam` - Online examination system
- `reports` - Report generation
- `store` - Store and inventory management
- `colleges` - College management
- `academic_years` - Academic year management
- `holidays` - Holiday management
- `system_settings` - System settings management

To add a new resource, edit `apps/core/permissions/registry.py`.

---

## 🔐 Default Roles and Permissions

### Superadmin
- Has access to **all colleges** without X-College-ID header
- Has access to **all resources** with **all scope**
- Bypasses all permission checks

### Admin / College Admin
- Full access to all resources within their college
- Scope: **all**

### Teacher
- Attendance: create, read, update, export (scope: **team**)
- Students: read (scope: **team**)
- Examinations: create, read, update, publish (scope: **team**)
- Online Exam: create, read, update, delete, publish, evaluate (scope: **team**)

### Student
- Attendance: read (scope: **mine**)
- Fees: read (scope: **mine**)
- Examinations: read (scope: **mine**)
- Library: read (scope: **mine**)

### HOD (Head of Department)
- Full access to all resources within their department
- Scope: **department**

### Staff
- Students: create, read, update, import, export (scope: **all**)
- Library: full access (scope: **all**)
- Hostel: full access (scope: **all**)

---

## 🔄 Team Membership Setup

For scope filtering to work with **team** scope, you need to create TeamMembership records:

```python
# Example: Assign students to a teacher
from apps.core.models import TeamMembership
from apps.accounts.models import User

teacher = User.objects.get(username='teacher1')
student = User.objects.get(username='student1')
college = College.objects.get(id=1)

TeamMembership.objects.create(
    college=college,
    leader=teacher,
    member=student,
    relationship_type='teacher_student',
    resource='attendance'
)
```

Or use the API:

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "X-College-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "leader": "teacher_user_id",
    "member": "student_user_id",
    "relationship_type": "teacher_student",
    "resource": "attendance"
  }' \
  http://localhost:8000/api/core/team-memberships/
```

---

## 🛠️ Customizing Permissions

### Via Django Admin or API

1. **Get the Permission record:**
   ```bash
   GET /api/core/permissions/?college=1&role=teacher
   ```

2. **Update the permissions_json:**
   ```json
   {
     "attendance": {
       "create": {"scope": "team", "enabled": true},
       "read": {"scope": "all", "enabled": true},
       "update": {"scope": "team", "enabled": true},
       "delete": {"scope": "none", "enabled": false},
       "export": {"scope": "department", "enabled": true}
     }
   }
   ```

3. **Save via API:**
   ```bash
   PATCH /api/core/permissions/{id}/
   ```

---

## 📊 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/core/permissions/` | GET | List all permissions |
| `/api/core/permissions/` | POST | Create permission configuration |
| `/api/core/permissions/{id}/` | GET/PUT/PATCH/DELETE | Manage specific permission |
| `/api/core/permissions/my-permissions/` | GET | Get current user's permissions |
| `/api/core/permissions/schema/` | GET | Get permission registry |
| `/api/core/team-memberships/` | GET | List team memberships |
| `/api/core/team-memberships/` | POST | Create team membership |
| `/api/core/team-memberships/{id}/` | GET/PUT/PATCH/DELETE | Manage specific membership |

---

## ⚠️ Important Notes

1. **Superadmin Bypass:**
   - Superadmins do NOT need X-College-ID header
   - They can access all colleges by not sending the header
   - Or send X-College-ID: all for explicit multi-college access

2. **Backward Compatibility:**
   - The permission system is **opt-in**
   - ViewSets without `resource_name` work as before
   - Existing functionality is preserved

3. **Migration Safety:**
   - Review migrations before applying
   - Backup your database first
   - Test on staging environment

4. **Performance:**
   - Permission checks are cached where possible
   - Scope filtering uses indexed queries
   - Minimal performance impact

---

## 🐛 Troubleshooting

### Issue: Migrations fail
**Solution:** Check for conflicting migrations. Run `python manage.py migrate --fake-initial` if needed.

### Issue: Superadmin gets 403 errors
**Solution:** Ensure `is_superadmin=True` and middleware is properly configured.

### Issue: Team scope returns no results
**Solution:** Create TeamMembership records for the leader and members.

### Issue: Permission changes don't take effect
**Solution:** Clear any caching, restart the server, or refetch permissions on frontend.

---

## 🎉 Next Steps

1. Apply migrations (Step 1 above)
2. Create superadmin user (Step 2 above)
3. Seed default permissions (Step 3 above)
4. Add `resource_name` to all your ViewSets
5. Set up team memberships
6. Test with different user roles
7. Customize permissions as needed

---

## 📚 Additional Resources

- **SOP Document:** See the detailed SOP provided for complete architecture
- **Permission Registry:** `apps/core/permissions/registry.py`
- **Permission Manager:** `apps/core/permissions/manager.py`
- **Scope Resolver:** `apps/core/permissions/scope_resolver.py`

---

**Implementation Date:** 2025-12-29
**Status:** ✅ Complete and Ready for Testing
