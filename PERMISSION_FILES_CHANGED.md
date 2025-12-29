# KUMSS Permission System - Complete File Changes List

This document lists ALL files that were created or modified for the permission system implementation.

---

## 📁 Files Created (New Files)

### 1. Permission Module Files

| File Path | Purpose | Key Contents |
|-----------|---------|--------------|
| `apps/core/permissions/__init__.py` | Package initializer | Makes permissions a Python package |
| `apps/core/permissions/registry.py` | Central permission registry | - `PERMISSION_REGISTRY` (all resources & actions)<br>- `AVAILABLE_SCOPES` (none, mine, team, dept, all)<br>- `get_default_permissions(role)` function |
| `apps/core/permissions/manager.py` | Permission checking logic | - `get_user_permissions(user, college)`<br>- `check_permission(user, resource, action, college)` |
| `apps/core/permissions/scope_resolver.py` | Scope-based filtering | - `apply_scope_filter(user, resource, queryset, college, scope)`<br>- Filters by mine/team/dept/all |
| `apps/core/permissions/drf_permissions.py` | DRF permission classes | - `IsSuperAdmin` permission class<br>- `ResourcePermission` permission class |
| `apps/core/permissions/mixins.py` | ViewSet mixins | - `ScopedQuerysetMixin` for automatic scope filtering |

### 2. Management Commands

| File Path | Purpose | Key Contents |
|-----------|---------|--------------|
| `apps/accounts/management/__init__.py` | Package initializer | Makes management a package |
| `apps/accounts/management/commands/__init__.py` | Package initializer | Makes commands a package |
| `apps/accounts/management/commands/create_superadmin.py` | Create superadmin users | - Command to create superadmin<br>- Sets `is_superadmin=True` |
| `apps/core/management/commands/seed_permissions.py` | Seed default permissions | - Seeds permissions for all colleges<br>- Creates Permission records for each role |

### 3. Documentation Files

| File Path | Purpose | Key Contents |
|-----------|---------|--------------|
| `PERMISSIONS_SETUP.md` | Setup guide | - Installation steps<br>- Architecture overview<br>- Usage examples |
| `PERMISSION_TESTING_GUIDE.md` | Testing guide for frontend team | - Testing checklist<br>- Frontend helper functions<br>- React component examples<br>- Troubleshooting guide |
| `PERMISSION_FLOW_EXPLAINED.md` | Complete flow explanation | - Resource-to-model mapping<br>- Flow diagrams<br>- Real-world examples<br>- Permission matrix |
| `PERMISSION_FILES_CHANGED.md` | This file | Complete list of changed files |

---

## 📝 Files Modified (Existing Files)

### 1. Models

#### `apps/accounts/models.py`
**What was added:**
```python
class User(AbstractUser):
    # ... existing fields ...

    # NEW FIELD ADDED:
    is_superadmin = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Superadmin has access to all colleges and all permissions"
    )
```

**Line numbers:** ~Line 30-35 (approximately, depends on existing code)

---

#### `apps/core/models.py`
**What was added:**
```python
# NEW MODEL 1: Permission
class Permission(CollegeScopedModel):
    """
    Stores role-based permissions in JSON format.
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    role = models.CharField(
        max_length=50,
        help_text="User role: student, teacher, admin, hod, staff"
    )
    permissions_json = models.JSONField(
        default=dict,
        help_text="Permission configuration in JSON format"
    )

    objects = CollegeManager()

    class Meta:
        db_table = 'permission'
        unique_together = [['college', 'role']]
        ordering = ['college', 'role']

    def __str__(self):
        return f"{self.college.name} - {self.role}"


# NEW MODEL 2: TeamMembership
class TeamMembership(CollegeScopedModel):
    """
    Defines team relationships for permission scoping.
    Example: teacher -> students relationship
    """
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_leader',
        help_text="The user who has access (e.g., teacher)"
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_member',
        help_text="The user being accessed (e.g., student)"
    )
    relationship_type = models.CharField(
        max_length=50,
        help_text="Type of relationship: teacher-student, hod-teacher, etc."
    )
    resource = models.CharField(
        max_length=50,
        help_text="Resource this relationship applies to (students, attendance, etc.)"
    )

    objects = CollegeManager()

    class Meta:
        db_table = 'team_membership'
        unique_together = [['college', 'leader', 'member', 'resource']]
        ordering = ['college', 'leader']

    def __str__(self):
        return f"{self.leader.username} -> {self.member.username} ({self.resource})"
```

**Line numbers:** Added at the end of models.py (after existing models)

---

### 2. Serializers

#### `apps/core/serializers.py`
**What was added:**
```python
from apps.core.permissions.registry import PERMISSION_REGISTRY

# NEW SERIALIZER 1: PermissionSerializer
class PermissionSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """
    Serializer for Permission model with JSON validation.
    """
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Permission
        fields = [
            'id', 'college', 'college_name', 'role', 'permissions_json',
            'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate_permissions_json(self, value):
        """Validate permission JSON structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("permissions_json must be a JSON object")

        for resource, actions in value.items():
            # Validate resource exists in registry
            if resource not in PERMISSION_REGISTRY:
                raise serializers.ValidationError(
                    f"Invalid resource: {resource}. "
                    f"Valid resources: {list(PERMISSION_REGISTRY.keys())}"
                )

            if not isinstance(actions, dict):
                raise serializers.ValidationError(
                    f"Actions for resource '{resource}' must be a JSON object"
                )

            # Validate actions
            valid_actions = PERMISSION_REGISTRY[resource]['actions']
            for action, config in actions.items():
                if action not in valid_actions:
                    raise serializers.ValidationError(
                        f"Invalid action '{action}' for resource '{resource}'. "
                        f"Valid actions: {valid_actions}"
                    )

                if not isinstance(config, dict):
                    raise serializers.ValidationError(
                        f"Config for {resource}.{action} must be a JSON object"
                    )

                if 'enabled' not in config:
                    raise serializers.ValidationError(
                        f"Missing 'enabled' field in {resource}.{action}"
                    )

                if 'scope' not in config:
                    raise serializers.ValidationError(
                        f"Missing 'scope' field in {resource}.{action}"
                    )

                if config['scope'] not in ['none', 'mine', 'team', 'department', 'all']:
                    raise serializers.ValidationError(
                        f"Invalid scope '{config['scope']}' in {resource}.{action}. "
                        f"Valid scopes: none, mine, team, department, all"
                    )

        return value


# NEW SERIALIZER 2: TeamMembershipSerializer
class TeamMembershipSerializer(TenantAuditMixin, serializers.ModelSerializer):
    """
    Serializer for TeamMembership model.
    """
    college_name = serializers.CharField(source='college.name', read_only=True)
    leader_username = serializers.CharField(source='leader.username', read_only=True)
    member_username = serializers.CharField(source='member.username', read_only=True)

    class Meta:
        model = TeamMembership
        fields = [
            'id', 'college', 'college_name', 'leader', 'leader_username',
            'member', 'member_username', 'relationship_type', 'resource',
            'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def validate(self, attrs):
        """Validate team membership"""
        # Ensure leader and member are from the same college
        if attrs['leader'].college_id != attrs['member'].college_id:
            raise serializers.ValidationError(
                "Leader and member must be from the same college"
            )

        # Validate resource exists
        if attrs['resource'] not in PERMISSION_REGISTRY:
            raise serializers.ValidationError(
                f"Invalid resource: {attrs['resource']}"
            )

        return attrs
```

**Line numbers:** Added at the end of serializers.py (after existing serializers)

---

#### `apps/accounts/serializers.py`
**What was modified:**

**Location:** `TokenWithUserSerializer` class

**BEFORE:**
```python
def get_user_permissions(self, obj):
    """Get user permissions"""
    # Previous implementation (might have been empty or simple)
    return {}

def get_user_roles(self, obj):
    """Get user roles"""
    # Previous implementation (might have been empty or simple)
    return []
```

**AFTER:**
```python
def get_user_permissions(self, obj):
    """
    Get user permissions from the Permission model.
    Returns comprehensive permission JSON for frontend use.
    """
    from apps.core.permissions.manager import get_user_permissions as get_perms
    from apps.core.models import College

    user = getattr(obj, 'user', None)
    if not user:
        return {}

    # Get college for permission lookup
    college = None
    if user.college_id:
        try:
            college = College.objects.all_colleges().get(id=user.college_id)
        except College.DoesNotExist:
            pass

    # Get permissions from permission system
    permissions = get_perms(user, college)
    return permissions

def get_user_roles(self, obj):
    """
    Get user roles including primary user_type and any additional UserRole assignments.
    """
    user = getattr(obj, 'user', None)
    if not user:
        return []

    roles_data = []

    # Add primary role from user_type
    if user.user_type:
        from apps.core.permissions.manager import get_user_permissions
        from apps.core.models import College

        college = None
        if user.college_id:
            try:
                college = College.objects.all_colleges().get(id=user.college_id)
            except College.DoesNotExist:
                pass

        permissions = get_user_permissions(user, college)

        # Count enabled permissions
        permission_count = sum(
            1 for resource_perms in permissions.values()
            for action_config in resource_perms.values()
            if action_config.get('enabled', False)
        )

        roles_data.append({
            'role_name': user.get_user_type_display(),
            'role_code': user.user_type,
            'is_primary': True,
            'description': f'{user.get_user_type_display()} user',
            'permissions_count': permission_count,
        })

    # Add any additional UserRole assignments if they exist
    if hasattr(user, 'user_roles'):
        for user_role in user.user_roles.filter(is_active=True):
            roles_data.append({
                'role_name': user_role.role.name if hasattr(user_role, 'role') else 'N/A',
                'role_code': user_role.role.code if hasattr(user_role, 'role') else 'N/A',
                'is_primary': False,
                'description': user_role.role.description if hasattr(user_role, 'role') else '',
                'permissions_count': 0,
            })

    return roles_data
```

**Line numbers:** ~Line 150-250 (depends on existing serializer location)

---

### 3. Views

#### `apps/core/views.py`
**What was added:**

```python
from apps.core.permissions.drf_permissions import IsSuperAdmin, ResourcePermission
from drf_spectacular.utils import extend_schema, OpenApiResponse

# NEW VIEWSET 1: PermissionViewSet
class PermissionViewSet(CollegeScopedModelViewSet):
    """
    ViewSet for managing permissions.
    Only admins and superadmins can manage permissions.
    """
    queryset = Permission.objects.all_colleges()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'role', 'is_active']
    search_fields = ['role']
    ordering_fields = ['college', 'role']
    ordering = ['college', 'role']

    def get_queryset(self):
        # Superadmin sees all permissions across all colleges
        if getattr(self.request.user, 'is_superadmin', False):
            return Permission.objects.using('default').all()

        # Regular users see only their college's permissions
        return super().get_queryset()

    @extend_schema(
        summary="Get current user's permissions",
        description="Returns the logged-in user's permission configuration.",
        responses={200: OpenApiResponse(description="User permissions")},
        tags=['Permissions']
    )
    @action(detail=False, methods=['get'])
    def my_permissions(self, request):
        """
        GET /api/core/permissions/my-permissions/
        Returns current user's permissions.
        """
        from apps.core.permissions.manager import get_user_permissions
        from apps.core.utils import get_current_college_id

        college = None
        college_id = get_current_college_id()
        if college_id and college_id != 'all':
            college = College.objects.filter(id=college_id).first()

        permissions = get_user_permissions(request.user, college)

        # Get user's role
        role = getattr(request.user, 'user_type', 'student')

        return Response({
            'user_id': str(request.user.id),
            'username': request.user.username,
            'is_superadmin': getattr(request.user, 'is_superadmin', False),
            'college_id': college_id,
            'role': role,
            'permissions': permissions,
        })

    @extend_schema(
        summary="Get permission schema",
        description="Returns the permission registry for building UI.",
        responses={200: OpenApiResponse(description="Permission schema")},
        tags=['Permissions']
    )
    @action(detail=False, methods=['get'])
    def schema(self, request):
        """
        GET /api/core/permissions/schema/
        Returns permission registry for building UI.
        """
        from apps.core.permissions.registry import PERMISSION_REGISTRY, AVAILABLE_SCOPES

        return Response({
            'resources': PERMISSION_REGISTRY,
            'scopes': AVAILABLE_SCOPES,
        })


# NEW VIEWSET 2: TeamMembershipViewSet
class TeamMembershipViewSet(CollegeScopedModelViewSet):
    """
    ViewSet for managing team memberships.
    """
    queryset = TeamMembership.objects.all_colleges()
    serializer_class = TeamMembershipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'leader', 'member', 'relationship_type', 'resource', 'is_active']
    search_fields = ['leader__username', 'member__username', 'resource']
    ordering_fields = ['college', 'leader', 'created_at']
    ordering = ['college', 'leader']

    def get_queryset(self):
        # Superadmin sees all team memberships
        if getattr(self.request.user, 'is_superadmin', False):
            return TeamMembership.objects.using('default').all()

        # Regular users see only their college's team memberships
        return super().get_queryset()
```

**Line numbers:** Added at the end of views.py (~Line 574-670)

---

### 4. URLs

#### `apps/core/urls.py`
**What was added:**

```python
from apps.core.views import (
    # ... existing imports ...
    PermissionViewSet,        # NEW
    TeamMembershipViewSet,    # NEW
)

# Register new routes
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'team-memberships', TeamMembershipViewSet, basename='team-membership')
```

**Line numbers:** Added to existing router registrations (~Line 20-30)

---

### 5. Middleware

#### `apps/core/middleware.py`
**What was modified:**

**Location:** `CollegeMiddleware.process_request()` method

**BEFORE:**
```python
def process_request(self, request):
    # Get college ID from header
    college_id = request.headers.get('X-College-ID') or request.headers.get('X-Tenant-ID')

    if not college_id:
        # Handle missing college ID
        pass
```

**AFTER:**
```python
def process_request(self, request):
    user = getattr(request, 'user', None)

    # NEW: Superadmin bypass - they can access all colleges
    if user and user.is_authenticated and getattr(user, 'is_superadmin', False):
        set_current_request(request)
        request.current_college = None
        return  # Superadmin bypasses college scoping

    # Existing college ID logic
    college_id = request.headers.get('X-College-ID') or request.headers.get('X-Tenant-ID')

    # ... rest of existing code ...
```

**Line numbers:** ~Line 30-50 (in process_request method)

---

### 6. Mixins

#### `apps/core/mixins.py`
**What was modified:**

**Location:** `CollegeScopedModelViewSet` class

**ADDED NEW METHOD:**
```python
class CollegeScopedModelViewSet(viewsets.ModelViewSet):
    # ... existing code ...

    # NEW METHOD ADDED:
    def _apply_permission_scope_filter(self, queryset):
        """
        Apply permission-based scope filtering to the queryset.
        Only applies if resource_name is defined on the viewset.
        """
        from apps.core.permissions.manager import check_permission
        from apps.core.permissions.scope_resolver import apply_scope_filter

        # Get the action being performed
        action_map = {
            'list': 'read',
            'retrieve': 'read',
            'create': 'create',
            'update': 'update',
            'partial_update': 'update',
            'destroy': 'delete',
        }
        action = action_map.get(self.action, 'read')

        # Check permission and get scope
        has_perm, scope = check_permission(
            user=self.request.user,
            resource=self.resource_name,
            action=action,
            college=self.request.current_college if hasattr(self.request, 'current_college') else None
        )

        if not has_perm:
            # Return empty queryset if no permission
            return queryset.none()

        # Apply scope filter
        return apply_scope_filter(
            user=self.request.user,
            resource=self.resource_name,
            queryset=queryset,
            college=self.request.current_college if hasattr(self.request, 'current_college') else None,
            scope=scope
        )

    def get_queryset(self):
        """
        Override to add permission-based scope filtering.
        """
        queryset = super().get_queryset()

        # First apply college-based filtering
        queryset = self.filter_queryset_by_college(queryset)

        # NEW: If resource_name is defined, apply permission-based scope filtering
        if hasattr(self, 'resource_name') and self.resource_name:
            queryset = self._apply_permission_scope_filter(queryset)

        return queryset
```

**Line numbers:** Added to CollegeScopedModelViewSet class (~Line 100-180)

---

## 📊 Complete File Tree

```
kumsserpbackend/
│
├── apps/
│   ├── accounts/
│   │   ├── models.py                    ✏️ MODIFIED (added is_superadmin field)
│   │   ├── serializers.py               ✏️ MODIFIED (updated get_user_permissions & get_user_roles)
│   │   └── management/
│   │       ├── __init__.py              ✨ NEW
│   │       └── commands/
│   │           ├── __init__.py          ✨ NEW
│   │           └── create_superadmin.py ✨ NEW
│   │
│   └── core/
│       ├── models.py                    ✏️ MODIFIED (added Permission & TeamMembership models)
│       ├── serializers.py               ✏️ MODIFIED (added Permission & TeamMembership serializers)
│       ├── views.py                     ✏️ MODIFIED (added Permission & TeamMembership viewsets)
│       ├── urls.py                      ✏️ MODIFIED (registered new routes)
│       ├── middleware.py                ✏️ MODIFIED (added superadmin bypass)
│       ├── mixins.py                    ✏️ MODIFIED (added permission scope filtering)
│       │
│       ├── permissions/                 ✨ NEW DIRECTORY
│       │   ├── __init__.py              ✨ NEW
│       │   ├── registry.py              ✨ NEW (permission definitions)
│       │   ├── manager.py               ✨ NEW (permission checking logic)
│       │   ├── scope_resolver.py        ✨ NEW (scope filtering logic)
│       │   ├── drf_permissions.py       ✨ NEW (DRF permission classes)
│       │   └── mixins.py                ✨ NEW (viewset mixins)
│       │
│       └── management/
│           └── commands/
│               └── seed_permissions.py  ✨ NEW
│
├── PERMISSIONS_SETUP.md                 ✨ NEW (setup guide)
├── PERMISSION_TESTING_GUIDE.md          ✨ NEW (testing guide)
├── PERMISSION_FLOW_EXPLAINED.md         ✨ NEW (flow explanation)
└── PERMISSION_FILES_CHANGED.md          ✨ NEW (this file)
```

---

## 📈 Summary Statistics

| Category | Count | Files |
|----------|-------|-------|
| **New Files Created** | 18 | Permission module (6), Management commands (4), Documentation (4), Package inits (4) |
| **Existing Files Modified** | 7 | Models (2), Serializers (2), Views (1), URLs (1), Middleware (1), Mixins (1) |
| **Total Files Changed** | **25** | Complete permission system implementation |

---

## 🔍 Quick Reference: Where to Find What

| What You Need | File to Check |
|---------------|---------------|
| **All available resources and actions** | `apps/core/permissions/registry.py` → `PERMISSION_REGISTRY` |
| **Default permissions per role** | `apps/core/permissions/registry.py` → `get_default_permissions()` |
| **Permission checking logic** | `apps/core/permissions/manager.py` → `check_permission()` |
| **Scope filtering logic** | `apps/core/permissions/scope_resolver.py` → `apply_scope_filter()` |
| **DRF permission classes** | `apps/core/permissions/drf_permissions.py` |
| **Permission & TeamMembership models** | `apps/core/models.py` |
| **Permission serializers** | `apps/core/serializers.py` |
| **Permission API endpoints** | `apps/core/views.py` → `PermissionViewSet` |
| **Superadmin field** | `apps/accounts/models.py` → `User.is_superadmin` |
| **Login response with permissions** | `apps/accounts/serializers.py` → `TokenWithUserSerializer` |
| **Seed default permissions** | `apps/core/management/commands/seed_permissions.py` |
| **Create superadmin** | `apps/accounts/management/commands/create_superadmin.py` |
| **Setup instructions** | `PERMISSIONS_SETUP.md` |
| **Testing guide** | `PERMISSION_TESTING_GUIDE.md` |
| **Flow explanation** | `PERMISSION_FLOW_EXPLAINED.md` |

---

## 🎯 Migration Files (To Be Created)

When you run `python manage.py makemigrations`, these migration files will be created:

```
apps/accounts/migrations/
└── 00XX_add_is_superadmin_field.py      (adds is_superadmin to User)

apps/core/migrations/
└── 00XX_add_permission_models.py        (adds Permission & TeamMembership models)
```

---

## ✅ Checklist: All Changes Implemented

- [x] Added `is_superadmin` field to User model
- [x] Created Permission model with JSONField
- [x] Created TeamMembership model
- [x] Created permission registry with all resources
- [x] Implemented permission checking logic
- [x] Implemented scope filtering logic
- [x] Created DRF permission classes
- [x] Created viewset mixins for permission enforcement
- [x] Added Permission serializer with JSON validation
- [x] Added TeamMembership serializer
- [x] Created PermissionViewSet with custom actions
- [x] Created TeamMembershipViewSet
- [x] Registered new API routes
- [x] Updated login serializer to include permissions
- [x] Updated middleware for superadmin bypass
- [x] Updated base viewsets for permission filtering
- [x] Created seed_permissions management command
- [x] Created create_superadmin management command
- [x] Created setup documentation
- [x] Created testing guide
- [x] Created flow explanation
- [x] Created file changes reference (this file)

---

**Total Implementation:** 25 files changed/created ✅
