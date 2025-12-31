# Role and Permission System - Complete Flow Documentation

## 📋 Overview

This document explains how roles are assigned to users and how permissions are linked to those roles in the KUMSS ERP system.

---

## 🔄 Complete Flow: User → Role → Permissions

### **1. User Creation & Role Assignment**

#### **Step 1: User Model (`apps/accounts/models.py`)**

When a user is created, they have a `user_type` field:

```python
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,  # Enum with predefined types
        default=UserType.STUDENT,
        help_text="User role/type in the system"
    )
```

**Available User Types** (Line 22-29):

```python
class UserType(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    COLLEGE_ADMIN = 'college_admin', 'College Admin'
    TEACHER = 'teacher', 'Teacher'
    STUDENT = 'student', 'Student'
    PARENT = 'parent', 'Parent'
    STAFF = 'staff', 'Support Staff'
```

---

### **2. Role Mapping: User Type → Permission Role**

#### **The Connection** (`apps/core/permissions/manager.py`, Lines 36-46)

The system maps `user_type` values to permission role names:

```python
role_mapping = {
    'super_admin': 'admin',           # Maps to 'admin' in registry.py
    'college_admin': 'college_admin', # Maps to 'college_admin' in registry.py
    'teacher': 'teacher',             # Maps to 'teacher' in registry.py
    'student': 'student',             # Maps to 'student' in registry.py
    'parent': 'student',              # Parents get same permissions as students
    'staff': 'staff',                 # Maps to 'staff' in registry.py
}
```

**This is the KEY connection!**

- User's `user_type` field → Mapped to permission role → Looks up in `registry.py`

---

### **3. Permission Lookup Flow**

#### **When a user tries to access a resource:**

```
User Request
    ↓
1. DRF Permission Class (drf_permissions.py)
    ↓
2. check_permission(user, resource, action, college)
    ↓
3. get_user_permissions(user, college)
    ↓
4. Get user.user_type → Map to role name
    ↓
5. Check if college has custom Permission model
    ↓
6. If not, get_default_permissions(role) from registry.py
    ↓
7. Return permission config for that role
    ↓
8. Check if action is enabled and get scope
    ↓
9. Allow/Deny access
```

---

## 🔐 Naming Conventions & Conflict Prevention

### **1. User Type Naming (Database Level)**

- **Location:** `apps/accounts/models.py` → `UserType` enum
- **Format:** `snake_case` (e.g., `super_admin`, `college_admin`)
- **Stored in:** `User.user_type` field in database
- **Constraint:** Must be one of the predefined `UserType.choices`

### **2. Permission Role Naming (Registry Level)**

- **Location:** `apps/core/permissions/registry.py` → `get_default_permissions()`
- **Format:** `snake_case` (e.g., `admin`, `teacher`, `student`)
- **Used in:** Permission configuration dictionaries

### **3. Conflict Prevention Mechanisms**

#### ✅ **No Naming Conflicts Because:**

1. **Enum Constraints:**

   ```python
   user_type = models.CharField(
       choices=UserType.choices,  # Only allows predefined values
   )
   ```

   - Users can ONLY have `user_type` values from the `UserType` enum
   - Database enforces this constraint

2. **Explicit Mapping:**

   ```python
   role_mapping = {
       'super_admin': 'admin',  # Explicit 1-to-1 mapping
       'college_admin': 'college_admin',
       # ... etc
   }
   ```

   - Clear, explicit mapping prevents ambiguity
   - If `user_type` doesn't exist in mapping, defaults to `'student'`

3. **Fallback Mechanism:**
   ```python
   role = role_mapping.get(role, 'student')  # Defaults to 'student'
   ```
   - Unknown roles default to least privileged (student)
   - Fail-safe approach

---

## 🎯 Two-Tier Permission System

### **Tier 1: Simple User Type (Default)**

Most users get permissions based on their `user_type`:

```
User.user_type = 'teacher'
    ↓
Mapped to role = 'teacher'
    ↓
get_default_permissions('teacher') from registry.py
    ↓
Returns teacher permissions (team-level access to attendance, exams, etc.)
```

### **Tier 2: College-Specific Customization (Advanced)**

Colleges can override default permissions using the `Permission` model:

```python
# apps/core/models.py (Lines 699-727)
class Permission(CollegeScopedModel):
    role = models.CharField(
        max_length=50,
        help_text="Role name (e.g., 'admin', 'teacher', 'student', 'hod')"
    )
    permissions_json = models.JSONField(
        default=dict,
        help_text="Permission configuration"
    )
```

**Flow with custom permissions:**

```
User.user_type = 'teacher' + College = 'ABC College'
    ↓
Check: Does Permission model have entry for (college='ABC', role='teacher')?
    ↓
YES → Use custom permissions_json from Permission model
NO  → Use default permissions from registry.py
```

---

## 📊 Complete Example

### **Example: Teacher User**

1. **User Created:**

   ```python
   user = User.objects.create(
       username='john_doe',
       user_type='teacher',  # From UserType.TEACHER
       college=abc_college
   )
   ```

2. **Permission Check:**

   ```python
   # User tries to create attendance
   check_permission(user, 'attendance', 'create', abc_college)
   ```

3. **Internal Flow:**

   ```python
   # Step 1: Get user_type
   user_type = 'teacher'

   # Step 2: Map to role
   role = role_mapping['teacher']  # Returns 'teacher'

   # Step 3: Check for college-specific permissions
   try:
       perm = Permission.objects.get(
           college=abc_college,
           role='teacher'
       )
       permissions = perm.permissions_json
   except Permission.DoesNotExist:
       # Step 4: Use defaults from registry.py
       permissions = get_default_permissions('teacher')
       # Returns:
       # {
       #     'attendance': {
       #         'create': {'scope': 'team', 'enabled': True},
       #         ...
       #     }
       # }

   # Step 5: Check specific permission
   enabled = permissions['attendance']['create']['enabled']  # True
   scope = permissions['attendance']['create']['scope']      # 'team'

   # Step 6: Return result
   return (True, 'team')  # User CAN create attendance for their team
   ```

---

## 🛡️ Security & Validation

### **1. Database Constraints**

- `user_type` must be from `UserType.choices` enum
- Cannot assign arbitrary role names

### **2. Permission Model Constraints**

```python
constraints = [
    models.UniqueConstraint(
        fields=['college', 'role'],
        name='unique_college_role_permission'
    )
]
```

- Each college can have only ONE permission config per role
- Prevents duplicate/conflicting permissions

### **3. Superadmin Bypass**

```python
if getattr(user, 'is_superadmin', False):
    return True, 'all'  # Always allowed
```

- Superadmins bypass all permission checks
- Ultimate failsafe for system administration

---

## 🔧 Adding New Roles

### **To add a new role (e.g., 'librarian'):**

1. **Add to UserType enum** (`apps/accounts/models.py`):

   ```python
   class UserType(models.TextChoices):
       # ... existing types ...
       LIBRARIAN = 'librarian', 'Librarian'
   ```

2. **Add to role mapping** (`apps/core/permissions/manager.py`):

   ```python
   role_mapping = {
       # ... existing mappings ...
       'librarian': 'librarian',
   }
   ```

3. **Add default permissions** (`apps/core/permissions/registry.py`):

   ```python
   def get_default_permissions(role):
       defaults = {
           # ... existing roles ...
           'librarian': {
               'library': {
                   'create': {'scope': 'all', 'enabled': True},
                   'read': {'scope': 'all', 'enabled': True},
                   # ... etc
               },
           },
       }
   ```

4. **Run migrations** (if needed):
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

---

## ✅ Summary: No Naming Conflicts!

**Why there are NO conflicts:**

1. ✅ **Enum-based user types** - Only predefined values allowed
2. ✅ **Explicit mapping** - Clear 1-to-1 relationship
3. ✅ **Fallback defaults** - Unknown roles → 'student'
4. ✅ **Database constraints** - Unique constraints prevent duplicates
5. ✅ **Two-tier system** - College overrides OR defaults
6. ✅ **Consistent naming** - All use `snake_case`

**The system is robust and conflict-free!** 🎉
