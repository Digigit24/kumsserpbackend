# Organizational Hierarchy System - Standard Operating Procedure (SOP)

## Executive Summary
This SOP defines the implementation of a dynamic organizational hierarchy system with role-based access control (RBAC), team management, and permission synchronization.

---

## 1. SYSTEM ARCHITECTURE

### 1.1 Core Components
```
┌─────────────────────────────────────────┐
│     Organizational Hierarchy Tree       │
│  (CEO → Principals → Teachers → etc.)   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         Dynamic Role System             │
│   (Roles with granular permissions)     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│          Team Management                │
│   (Auto-assignment based on hierarchy)  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│      Permission Enforcement             │
│    (Synced across all operations)       │
└─────────────────────────────────────────┘
```

---

## 2. DATABASE SCHEMA DESIGN

### 2.1 OrganizationNode (Tree Structure)
```python
class OrganizationNode(models.Model):
    """
    MPTT-based tree structure for organization hierarchy
    Uses django-mptt for efficient tree queries
    """
    # Basic Info
    name = CharField(max_length=255)  # "CEO", "Principal - College A"
    node_type = CharField(choices=NODE_TYPES)  # ceo, principal, hod, teacher, staff
    description = TextField(blank=True)

    # Tree Structure (MPTT fields auto-added)
    parent = TreeForeignKey('self', null=True, blank=True)

    # Linked Entity (optional - if node represents actual user/college)
    user = ForeignKey(User, null=True, blank=True)
    college = ForeignKey(College, null=True, blank=True)

    # Role Assignment
    role = ForeignKey('DynamicRole', null=True)

    # Metadata
    is_active = BooleanField(default=True)
    order = IntegerField(default=0)  # Display order among siblings

    class MPTTMeta:
        order_insertion_by = ['order', 'name']
```

### 2.2 DynamicRole (Role System)
```python
class DynamicRole(models.Model):
    """
    Flexible role definition - NOT hardcoded
    """
    name = CharField(max_length=100, unique=True)  # "College Administrator", "Teacher Level 1"
    code = SlugField(max_length=50, unique=True)
    description = TextField(blank=True)

    # Role Hierarchy Level
    level = IntegerField(default=0)  # Higher = more authority

    # College-specific or global
    college = ForeignKey(College, null=True, blank=True)
    is_global = BooleanField(default=False)  # CEO, central manager roles

    # Metadata
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
```

### 2.3 Permission (Granular Permissions)
```python
class Permission(models.Model):
    """
    Granular permission system
    Format: app.action_resource
    Example: students.view_student, fees.create_invoice
    """
    code = CharField(max_length=100, unique=True)  # "students.create"
    name = CharField(max_length=255)  # "Create Student"
    app_label = CharField(max_length=50)  # "students"
    resource = CharField(max_length=50)  # "student"
    action = CharField(max_length=20)  # view, create, update, delete, approve

    description = TextField(blank=True)
    category = CharField(max_length=50)  # "Academic", "Financial", "Administrative"
```

### 2.4 RolePermission (Many-to-Many)
```python
class RolePermission(models.Model):
    """
    Links roles to permissions - THIS IS DYNAMIC
    Frontend can add/remove permissions from roles
    """
    role = ForeignKey(DynamicRole, on_delete=models.CASCADE)
    permission = ForeignKey(Permission, on_delete=models.CASCADE)

    # Permission modifiers
    can_delegate = BooleanField(default=False)  # Can assign this permission to others
    scope = CharField(max_length=20, default='college')  # college, department, self

    class Meta:
        unique_together = [['role', 'permission']]
```

### 2.5 Team (Team Management)
```python
class Team(models.Model):
    """
    Teams are auto-created based on hierarchy nodes
    """
    name = CharField(max_length=255)  # "Principal Team - College A"
    node = OneToOneField(OrganizationNode)  # Team belongs to a node

    # Team Lead (the person at that node)
    lead_user = ForeignKey(User, related_name='leading_teams', null=True)

    # Team Description
    description = TextField(blank=True)
    team_type = CharField(max_length=50)  # principal_team, teacher_team, department_team

    # College scope
    college = ForeignKey(College, null=True)

    # Metadata
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
```

### 2.6 TeamMember (Team Membership)
```python
class TeamMember(models.Model):
    """
    Users belong to teams - AUTO-ASSIGNED based on hierarchy
    """
    team = ForeignKey(Team, on_delete=models.CASCADE)
    user = ForeignKey(User, on_delete=models.CASCADE)

    # Membership details
    role_in_team = CharField(max_length=50)  # member, coordinator, deputy
    joined_at = DateTimeField(auto_now_add=True)

    # Auto-assignment tracking
    auto_assigned = BooleanField(default=False)
    assignment_reason = TextField(blank=True)  # "Student under teacher", "Teacher under principal"

    class Meta:
        unique_together = [['team', 'user']]
```

### 2.7 UserRole (User Role Assignment)
```python
class UserRole(models.Model):
    """
    Users can have multiple roles
    """
    user = ForeignKey(User, on_delete=models.CASCADE)
    role = ForeignKey(DynamicRole, on_delete=models.CASCADE)

    # Scope limitations
    college = ForeignKey(College, null=True, blank=True)
    department = ForeignKey(Department, null=True, blank=True)

    # Validity period
    valid_from = DateField(null=True)
    valid_until = DateField(null=True)

    # Assignment tracking
    assigned_by = ForeignKey(User, related_name='role_assignments_made')
    assigned_at = DateTimeField(auto_now_add=True)

    is_active = BooleanField(default=True)

    class Meta:
        unique_together = [['user', 'role', 'college']]
```

---

## 3. IMPLEMENTATION PHASES

### Phase 1: Core Models & Migrations
**Files to create:**
- `apps/core/models/organization.py` - OrganizationNode
- `apps/core/models/roles.py` - DynamicRole, Permission, RolePermission
- `apps/core/models/teams.py` - Team, TeamMember, UserRole
- Migrations for all models

**Key decisions:**
- Use `django-mptt` for tree structure (efficient queries)
- Use generic ForeignKey for node linking (user, college, department)
- Permissions format: `{app}.{action}_{resource}`

### Phase 2: Auto-Assignment Logic
**Business Rules:**

1. **Student Created** → Auto-assign to:
   - Class Teacher's team
   - Section Coordinator's team (if exists)
   - Department Head's team (indirect)

2. **Teacher Created** → Auto-assign to:
   - Department Head's team
   - Principal's team (if principal role exists)

3. **Staff Created** → Auto-assign to:
   - Direct manager's team
   - Department team

**Implementation:**
```python
# apps/core/services/team_service.py

class TeamAutoAssignmentService:
    """
    Handles automatic team assignment based on hierarchy
    """

    @staticmethod
    def assign_student_to_teams(student):
        """
        When student is created/updated:
        1. Find their class teacher
        2. Find teacher's team
        3. Add student to team
        """
        class_teacher = student.section.class_teacher
        if class_teacher and class_teacher.user:
            teacher_teams = Team.objects.filter(
                lead_user=class_teacher.user,
                team_type='teacher_team'
            )
            for team in teacher_teams:
                TeamMember.objects.get_or_create(
                    team=team,
                    user=student.user,
                    defaults={
                        'auto_assigned': True,
                        'assignment_reason': f'Student in {class_teacher.name}\'s class'
                    }
                )

    @staticmethod
    def assign_teacher_to_teams(teacher):
        """
        When teacher is created:
        1. Find department head
        2. Find principal
        3. Add to their teams
        """
        # Implementation here
        pass
```

### Phase 3: Permission Checking System
**Middleware & Decorators:**

```python
# apps/core/permissions/checker.py

class PermissionChecker:
    """
    Real-time permission checking
    """

    def __init__(self, user):
        self.user = user
        self._permission_cache = None

    def has_permission(self, permission_code, college=None):
        """
        Check if user has permission
        Format: "students.create", "fees.approve_invoice"
        """
        if self.user.is_superuser:
            return True

        # Get user's roles
        user_roles = UserRole.objects.filter(
            user=self.user,
            is_active=True
        ).select_related('role')

        # Check if any role has the permission
        for user_role in user_roles:
            if self._role_has_permission(user_role.role, permission_code, college):
                return True

        return False

    def _role_has_permission(self, role, permission_code, college):
        """Check if role has specific permission"""
        return RolePermission.objects.filter(
            role=role,
            permission__code=permission_code
        ).exists()

    def get_user_permissions(self):
        """Get all permissions for user - CACHED"""
        if self._permission_cache is not None:
            return self._permission_cache

        # Query and cache
        permissions = Permission.objects.filter(
            rolepermission__role__userrole__user=self.user,
            rolepermission__role__userrole__is_active=True
        ).distinct()

        self._permission_cache = list(permissions.values_list('code', flat=True))
        return self._permission_cache
```

**DRF Permission Class:**
```python
# apps/core/permissions/api.py

class HasPermission(BasePermission):
    """
    DRF permission class
    Usage: permission_classes = [HasPermission('students.create')]
    """

    def __init__(self, permission_code):
        self.permission_code = permission_code

    def has_permission(self, request, view):
        checker = PermissionChecker(request.user)
        return checker.has_permission(self.permission_code)
```

### Phase 4: Frontend API Endpoints

**Required APIs:**

1. **Organization Tree API**
```
GET /api/v1/organization/tree/
Response: Full tree structure with roles

GET /api/v1/organization/nodes/
Response: List of nodes (with filters)

POST /api/v1/organization/nodes/
Body: {name, node_type, parent_id, role_id}

PATCH /api/v1/organization/nodes/{id}/
Body: {role_id, is_active}

DELETE /api/v1/organization/nodes/{id}/
```

2. **Role Management API**
```
GET /api/v1/roles/
Response: List of all roles

POST /api/v1/roles/
Body: {name, description, level, permissions: []}

PATCH /api/v1/roles/{id}/permissions/
Body: {add: [perm_ids], remove: [perm_ids]}
```

3. **Permission API**
```
GET /api/v1/permissions/
Response: All available permissions

GET /api/v1/permissions/by-category/
Response: Permissions grouped by category
```

4. **Team API**
```
GET /api/v1/teams/
Response: User's teams

GET /api/v1/teams/{id}/members/
Response: Team members

POST /api/v1/teams/{id}/members/
Body: {user_id}  # Manual add
```

5. **User Role Assignment API**
```
POST /api/v1/users/{id}/roles/
Body: {role_id, college_id}

DELETE /api/v1/users/{id}/roles/{role_id}/
```

### Phase 5: Permission Sync Mechanism

**Real-time sync when role permissions change:**

```python
# apps/core/signals/role_signals.py

@receiver(post_save, sender=RolePermission)
def sync_role_permissions(sender, instance, created, **kwargs):
    """
    When role permissions change:
    1. Clear permission cache for all users with this role
    2. Send websocket notification to active users
    3. Log change for audit
    """
    from django.core.cache import cache

    # Clear cache for all users with this role
    users = User.objects.filter(
        userrole__role=instance.role,
        userrole__is_active=True
    )

    for user in users:
        cache_key = f'user_permissions_{user.id}'
        cache.delete(cache_key)

    # Notify active sessions
    # Send via SSE or WebSocket
```

---

## 4. MIGRATION FROM EXISTING SYSTEM

### 4.1 User Type Mapping
```python
# Migration script
ROLE_MAPPING = {
    'super_admin': 'CEO',
    'central_manager': 'Central Administrator',
    'college_admin': 'Principal',
    'teacher': 'Teacher',
    'student': 'Student',
    'accountant': 'Accountant',
    'librarian': 'Librarian',
}

def migrate_existing_users():
    """Create default roles and assign to existing users"""
    for user in User.objects.all():
        old_type = user.user_type
        role_name = ROLE_MAPPING.get(old_type)

        if role_name:
            role, _ = DynamicRole.objects.get_or_create(
                code=old_type,
                defaults={'name': role_name}
            )

            UserRole.objects.create(
                user=user,
                role=role,
                college=user.college,
                assigned_by=user,  # Self-assigned during migration
            )
```

---

## 5. FRONTEND INTEGRATION

### 5.1 Tree Visualization
**Recommended Library:** `react-organizational-chart` or `d3-org-chart`

**API Response Format:**
```json
{
  "id": 1,
  "name": "CEO",
  "node_type": "ceo",
  "role": {
    "id": 1,
    "name": "Chief Executive Officer",
    "permissions_count": 150
  },
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "ceo@example.com"
  },
  "children": [
    {
      "id": 2,
      "name": "Principal - College A",
      "node_type": "principal",
      "role": {...},
      "user": {...},
      "team_members_count": 45,
      "children": [...]
    }
  ]
}
```

### 5.2 Role Assignment Flow
```
1. Frontend clicks on node
2. GET /api/v1/organization/nodes/{id}/ - Get node details
3. Display modal with:
   - Current role
   - Available roles dropdown
   - Permissions preview
4. User selects new role
5. PATCH /api/v1/organization/nodes/{id}/ {role_id: X}
6. Backend updates node
7. Backend triggers permission sync
8. Frontend refreshes tree
```

### 5.3 Permission Management UI
```
1. GET /api/v1/roles/{id}/
2. Display role details with permissions list
3. Show checkboxes for each permission category
4. User toggles permissions
5. PATCH /api/v1/roles/{id}/permissions/
   Body: {
     add: [perm_id_1, perm_id_2],
     remove: [perm_id_3]
   }
6. Backend updates RolePermission records
7. Backend triggers sync for all users with this role
8. Show success message
```

---

## 6. SECURITY CONSIDERATIONS

### 6.1 Permission Validation
- Every API endpoint must check permissions
- Use decorators: `@require_permission('students.create')`
- Check in ViewSet methods
- Validate scope (college, department, self)

### 6.2 Audit Logging
```python
class PermissionAuditLog(models.Model):
    """Track all permission changes"""
    user = ForeignKey(User)
    action = CharField()  # granted, revoked, role_assigned
    role = ForeignKey(DynamicRole, null=True)
    permission = ForeignKey(Permission, null=True)
    target_user = ForeignKey(User, null=True)
    timestamp = DateTimeField(auto_now_add=True)
    ip_address = GenericIPAddressField()
```

### 6.3 Prevent Privilege Escalation
```python
def assign_role_to_user(assigner, target_user, role):
    """
    Only allow role assignment if:
    1. Assigner has 'users.assign_role' permission
    2. Assigner's role level >= target role level
    3. Role is within assigner's scope (college)
    """
    checker = PermissionChecker(assigner)

    if not checker.has_permission('users.assign_role'):
        raise PermissionDenied("No permission to assign roles")

    assigner_max_level = UserRole.objects.filter(
        user=assigner
    ).aggregate(Max('role__level'))['role__level__max']

    if role.level > assigner_max_level:
        raise PermissionDenied("Cannot assign role with higher level")
```

---

## 7. TESTING STRATEGY

### 7.1 Unit Tests
- Permission checking logic
- Team auto-assignment
- Role hierarchy validation
- Tree traversal queries

### 7.2 Integration Tests
- User creation → Team assignment flow
- Role change → Permission sync flow
- Permission check → API access flow

### 7.3 Performance Tests
- Tree loading with 1000+ nodes
- Permission check with 100+ roles
- Cache effectiveness

---

## 8. CACHING STRATEGY

```python
CACHES = {
    'default': {...},
    'permissions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'KEY_PREFIX': 'perms',
        'TIMEOUT': 3600,  # 1 hour
    }
}

# Cache user permissions
cache_key = f'user_perms_{user.id}'
permissions = cache.get(cache_key)
if not permissions:
    permissions = PermissionChecker(user).get_user_permissions()
    cache.set(cache_key, permissions, timeout=3600)
```

---

## 9. IMPLEMENTATION CHECKLIST

### Phase 1: Models (Week 1)
- [ ] Create OrganizationNode model with django-mptt
- [ ] Create DynamicRole model
- [ ] Create Permission model with seed data
- [ ] Create RolePermission model
- [ ] Create Team model
- [ ] Create TeamMember model
- [ ] Create UserRole model
- [ ] Run migrations
- [ ] Create seed data for default permissions

### Phase 2: Services (Week 2)
- [ ] TeamAutoAssignmentService
- [ ] PermissionChecker service
- [ ] RoleManagementService
- [ ] OrganizationTreeService
- [ ] Add signals for auto-assignment
- [ ] Add signals for permission sync

### Phase 3: APIs (Week 2-3)
- [ ] OrganizationNode ViewSet (CRUD + tree)
- [ ] DynamicRole ViewSet (CRUD + permissions)
- [ ] Permission ViewSet (Read-only)
- [ ] Team ViewSet (CRUD + members)
- [ ] UserRole ViewSet (Assign/Revoke)
- [ ] Add permission decorators to all endpoints

### Phase 4: Migration (Week 3)
- [ ] Write migration script for existing users
- [ ] Create default roles from user_types
- [ ] Assign roles to existing users
- [ ] Create default organization tree
- [ ] Test data integrity

### Phase 5: Testing (Week 4)
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Performance testing
- [ ] Security audit

---

## 10. RECOMMENDATIONS

### 10.1 Use Django Packages
```
pip install django-mptt  # Tree structure
pip install django-guardian  # Object-level permissions (optional)
pip install django-rules  # Rule-based permissions
```

### 10.2 API Response Caching
- Cache tree structure for 5 minutes
- Cache user permissions for 1 hour
- Invalidate on role/permission changes

### 10.3 Database Indexes
```sql
CREATE INDEX idx_userrole_user_active ON core_userrole(user_id, is_active);
CREATE INDEX idx_rolepermission_role ON core_rolepermission(role_id);
CREATE INDEX idx_team_member_user ON core_teammember(user_id);
CREATE INDEX idx_org_node_parent ON core_organizationnode(parent_id);
```

### 10.4 Monitoring
- Track permission check performance
- Monitor cache hit rates
- Log all permission changes
- Alert on failed permission checks

---

## 11. DECISION LOG

### Why MPTT over Adjacency List?
- Faster tree traversal
- Single query to get all descendants
- Better for read-heavy operations

### Why Dynamic Roles instead of hardcoded?
- Frontend can create new roles
- Permissions can be modified without code changes
- Supports multi-tenant scenarios

### Why Auto-Assignment?
- Reduces manual work
- Ensures consistency
- Maintains hierarchy integrity

### Why Cache Permissions?
- Permission checks on every API call
- Reduces DB queries significantly
- 1-hour cache is safe with sync mechanism

---

## 12. FUTURE ENHANCEMENTS

1. **Delegation System** - Allow temporary permission delegation
2. **Workflow Engine** - Approval workflows based on hierarchy
3. **Analytics Dashboard** - Org chart metrics
4. **Import/Export** - Bulk role assignments via CSV
5. **Role Templates** - Pre-defined role templates for common positions

---

## APPENDIX A: Sample Permission List

```python
PERMISSIONS = [
    # Students
    'students.view_student',
    'students.create_student',
    'students.update_student',
    'students.delete_student',
    'students.promote_student',

    # Fees
    'fees.view_invoice',
    'fees.create_invoice',
    'fees.approve_invoice',
    'fees.collect_payment',

    # Academic
    'academic.create_class',
    'academic.assign_teacher',
    'academic.view_timetable',
    'academic.update_timetable',

    # Reports
    'reports.view_financial',
    'reports.view_academic',
    'reports.export_data',

    # System
    'system.manage_roles',
    'system.manage_users',
    'system.view_audit_log',
]
```

---

**Document Version:** 1.0
**Last Updated:** 2025-01-09
**Status:** Ready for Implementation
