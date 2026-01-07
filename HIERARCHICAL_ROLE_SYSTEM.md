# Hierarchical Role System Implementation

## Overview

Organizational hierarchy-based role and permission system with dynamic role creation, parent-child relationships, and automatic team determination.

---

## Current System Analysis

### Existing Components
- **Role Model** (`apps/accounts/models.py`) - Basic roles without hierarchy
- **UserRole Model** - User-to-role assignments
- **Permission Model** (`apps/core/models.py`) - Resource-action permissions
- **TeamMembership Model** - Leader-member relationships

### Current Limitations
1. ❌ No parent-child role relationships
2. ❌ No organizational position hierarchy
3. ❌ Teams not auto-determined by hierarchy
4. ❌ No role tree visualization APIs

---

## Implementation Plan

### 1. Database Changes

#### Role Model Updates
**File**: `apps/accounts/models.py`

```python
class Role(CollegeScopedModel):
    # Existing fields
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    permissions = models.JSONField(default=dict)
    display_order = models.IntegerField(default=0)

    # NEW FIELDS
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent role in organizational hierarchy"
    )
    is_organizational_position = models.BooleanField(
        default=True,
        help_text="Whether this is an organizational position"
    )
    level = models.IntegerField(
        default=0,
        help_text="Hierarchy level (0=top, increases downward)"
    )

    # NEW METHODS
    def get_descendants(self, include_self=False):
        """Get all child roles recursively"""

    def get_ancestors(self, include_self=False):
        """Get all parent roles recursively"""

    def get_team_members(self):
        """Get all users under this role in hierarchy"""

    def save(self, *args, **kwargs):
        """Auto-calculate level based on parent"""
```

#### Migration Required
- Add `parent`, `is_organizational_position`, `level` fields to Role
- Update existing roles to set default values

---

### 2. New APIs

#### A. Role Tree API
**Endpoint**: `GET /api/v1/accounts/roles/tree/`

**Response**:
```json
{
  "tree": [
    {
      "id": "uuid",
      "name": "Principal",
      "code": "PRINCIPAL",
      "level": 0,
      "parent": null,
      "children": [
        {
          "id": "uuid",
          "name": "HOD",
          "code": "HOD",
          "level": 1,
          "parent": "principal-uuid",
          "children": [
            {
              "id": "uuid",
              "name": "Class Coordinator",
              "code": "CLASS_COORD",
              "level": 2,
              "parent": "hod-uuid",
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

#### B. Add Child Role API
**Endpoint**: `POST /api/v1/accounts/roles/{role_id}/add_child/`

**Request**:
```json
{
  "name": "Department Head",
  "code": "DEPT_HEAD",
  "description": "Department head role",
  "permissions": {}
}
```

**Response**:
```json
{
  "id": "uuid",
  "name": "Department Head",
  "parent": "parent-role-uuid",
  "level": 2,
  "created": true
}
```

#### C. Get Team Members API
**Endpoint**: `GET /api/v1/accounts/roles/{role_id}/team_members/`

**Response**:
```json
{
  "role": "HOD",
  "team_members": [
    {
      "user_id": "uuid",
      "name": "John Doe",
      "role": "Teacher",
      "level": 2
    }
  ],
  "total": 15
}
```

#### D. Get Hierarchy Path API
**Endpoint**: `GET /api/v1/accounts/roles/{role_id}/hierarchy_path/`

**Response**:
```json
{
  "path": [
    {"id": "uuid", "name": "Principal", "level": 0},
    {"id": "uuid", "name": "HOD", "level": 1},
    {"id": "uuid", "name": "Class Coordinator", "level": 2}
  ]
}
```

---

### 3. Backend Code Changes

#### A. Update Role Model
**File**: `apps/accounts/models.py`

Add fields and methods for hierarchy management.

#### B. Update Role Serializer
**File**: `apps/accounts/serializers.py`

```python
class RoleTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description',
            'parent', 'parent_name', 'level',
            'is_organizational_position', 'children'
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return RoleTreeSerializer(children, many=True).data
```

#### C. Update RoleViewSet
**File**: `apps/accounts/views.py`

```python
class RoleViewSet(CollegeScopedModelViewSet):
    # ... existing code

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get hierarchical role tree"""

    @action(detail=True, methods=['post'])
    def add_child(self, request, pk=None):
        """Add child role to this role"""

    @action(detail=True, methods=['get'])
    def team_members(self, request, pk=None):
        """Get all team members under this role"""

    @action(detail=True, methods=['get'])
    def hierarchy_path(self, request, pk=None):
        """Get ancestors path from root to this role"""
```

#### D. Auto-Update TeamMembership
**File**: `apps/core/signals.py` (new file)

```python
@receiver(post_save, sender=UserRole)
def update_team_membership_on_role_assignment(sender, instance, created, **kwargs):
    """
    Auto-create TeamMembership when user assigned to hierarchical role
    """
    if created and instance.role.parent:
        # Find parent role users
        # Create TeamMembership entries
```

---

### 4. Frontend Changes

#### A. Admin Dashboard - Role Tree Component

**New Page**: `/admin/roles/hierarchy`

**Features**:
1. **Tree Visualization**
   - Expandable/collapsible tree
   - Drag-and-drop to reorganize
   - Visual hierarchy levels

2. **Role Management**
   - Add new role (as root or child)
   - Edit role details
   - Delete role (with cascade warning)
   - Move role to different parent

3. **Permission Management**
   - Inline permission editor
   - Inherit permissions from parent option
   - Override specific permissions

4. **Team View**
   - Click role → show team members
   - Visualize reporting structure
   - Assign users to roles

#### B. API Integration

```javascript
// Fetch role tree
const fetchRoleTree = async () => {
  const response = await axios.get('/api/v1/accounts/roles/tree/');
  return response.data.tree;
};

// Add child role
const addChildRole = async (parentId, roleData) => {
  const response = await axios.post(
    `/api/v1/accounts/roles/${parentId}/add_child/`,
    roleData
  );
  return response.data;
};

// Get team members
const getTeamMembers = async (roleId) => {
  const response = await axios.get(
    `/api/v1/accounts/roles/${roleId}/team_members/`
  );
  return response.data.team_members;
};
```

#### C. UI Components Needed

1. **RoleTreeView** - Tree visualization with react-tree or similar
2. **RoleNodeEditor** - Edit role properties
3. **PermissionMatrix** - Visual permission grid
4. **TeamMemberList** - List of users under role
5. **HierarchyBreadcrumb** - Show role path

---

## Database Schema

### Role Table (Updated)

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| college_id | UUID | Foreign key to College |
| parent_id | UUID | Self-referencing FK (nullable) |
| name | VARCHAR(100) | Role name |
| code | VARCHAR(50) | Unique code |
| description | TEXT | Description |
| permissions | JSONB | Permission config |
| is_organizational_position | BOOLEAN | Is org position |
| level | INTEGER | Hierarchy level |
| display_order | INTEGER | Display order |
| is_active | BOOLEAN | Soft delete flag |
| created_at | TIMESTAMP | Created timestamp |
| updated_at | TIMESTAMP | Updated timestamp |

### Indexes Needed

```sql
CREATE INDEX idx_role_parent ON role(parent_id);
CREATE INDEX idx_role_level ON role(level);
CREATE INDEX idx_role_college_parent ON role(college_id, parent_id);
```

---

## Example Hierarchy

```
Principal (Level 0)
├── Vice Principal (Level 1)
│   ├── Academic Coordinator (Level 2)
│   └── Admin Coordinator (Level 2)
├── HOD - Computer Science (Level 1)
│   ├── Class Coordinator - CS Year 1 (Level 2)
│   ├── Class Coordinator - CS Year 2 (Level 2)
│   └── Lab Coordinator (Level 2)
├── HOD - Electronics (Level 1)
│   ├── Class Coordinator - EC Year 1 (Level 2)
│   └── Class Coordinator - EC Year 2 (Level 2)
└── Central Store Manager (Level 1)
    ├── Store Keeper - Building A (Level 2)
    └── Store Keeper - Building B (Level 2)
```

---

## Permission Inheritance

### Rules
1. **Default**: Child roles inherit parent permissions
2. **Override**: Child can have more restrictive permissions (never more permissive)
3. **Scope**: Child scope cannot exceed parent scope

### Example
```
Principal:
  - students: {read: {scope: "all", enabled: true}}

HOD (inherits from Principal):
  - students: {read: {scope: "department", enabled: true}}  ✓ Valid (more restrictive)

Class Coordinator (inherits from HOD):
  - students: {read: {scope: "team", enabled: true}}  ✓ Valid (more restrictive)
```

---

## Team Auto-Determination Logic

### How Teams are Built

1. **User assigned to role** → Trigger
2. **Find role's descendants** → All child roles
3. **Find users in descendant roles** → Team members
4. **Create TeamMembership entries** → Auto-populate

### Example
```
HOD assigned to "CS Department" role
  ↓
Find all child roles (Class Coordinators, Teachers in CS)
  ↓
Find all users in those roles
  ↓
Create TeamMembership(leader=HOD, member=Teacher, relationship_type='hod_faculty')
```

---

## Migration Strategy

### Phase 1: Database
1. Create migration for new Role fields
2. Set default values for existing roles
3. Build initial hierarchy for test college

### Phase 2: Backend APIs
1. Implement tree endpoint
2. Implement add_child endpoint
3. Implement team_members endpoint
4. Add signals for auto team updates

### Phase 3: Frontend
1. Create role tree page
2. Implement tree visualization
3. Add role creation/editing
4. Add permission management UI

### Phase 4: Testing
1. Test hierarchy queries
2. Test team auto-creation
3. Test permission inheritance
4. Load testing with deep hierarchies

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/accounts/roles/` | List all roles |
| GET | `/api/v1/accounts/roles/tree/` | Get hierarchical tree |
| GET | `/api/v1/accounts/roles/{id}/` | Get role details |
| POST | `/api/v1/accounts/roles/` | Create new root role |
| POST | `/api/v1/accounts/roles/{id}/add_child/` | Add child role |
| PUT | `/api/v1/accounts/roles/{id}/` | Update role |
| DELETE | `/api/v1/accounts/roles/{id}/` | Delete role |
| GET | `/api/v1/accounts/roles/{id}/team_members/` | Get team members |
| GET | `/api/v1/accounts/roles/{id}/hierarchy_path/` | Get ancestors path |
| GET | `/api/v1/accounts/roles/{id}/descendants/` | Get all descendants |

---

## Security Considerations

1. **Role Assignment**: Only superadmin or college_admin can assign roles
2. **Hierarchy Modification**: Only superadmin can modify hierarchy structure
3. **Permission Override**: Child cannot have broader scope than parent
4. **Circular References**: Prevent role from being its own ancestor
5. **Orphan Prevention**: Handle role deletion with cascade or reassignment

---

## Performance Optimization

### Strategies
1. **Level Denormalization**: Store level to avoid recursive queries
2. **Materialized Path**: Consider storing full path as string
3. **Caching**: Cache role trees per college
4. **Eager Loading**: Use `select_related('parent')` and `prefetch_related('children')`
5. **Query Limit**: Limit hierarchy depth to prevent deep recursion

### Example Queries
```python
# Efficient tree query
roles = Role.objects.filter(college=college, parent__isnull=True) \
    .prefetch_related('children__children__children')

# Get all descendants using level
descendants = Role.objects.filter(
    college=college,
    level__gt=role.level
)
```

---

## Files to Create/Modify

### New Files
1. `apps/accounts/migrations/XXXX_add_role_hierarchy.py`
2. `apps/core/signals.py`

### Modified Files
1. `apps/accounts/models.py` - Add Role hierarchy fields
2. `apps/accounts/serializers.py` - Add RoleTreeSerializer
3. `apps/accounts/views.py` - Add tree/hierarchy actions
4. `apps/accounts/admin.py` - Update admin interface

---

## Frontend Component Structure

```
admin/
├── roles/
│   ├── RoleHierarchy.jsx          # Main page
│   ├── components/
│   │   ├── RoleTree.jsx           # Tree visualization
│   │   ├── RoleNode.jsx           # Single role node
│   │   ├── RoleEditor.jsx         # Edit role modal
│   │   ├── AddRoleModal.jsx       # Add role modal
│   │   ├── PermissionMatrix.jsx   # Permission grid
│   │   └── TeamMemberList.jsx     # Team members list
│   └── hooks/
│       ├── useRoleTree.js         # Fetch role tree
│       └── useRoleActions.js      # CRUD actions
```

---

## Testing Checklist

- [ ] Create root role
- [ ] Create child role
- [ ] Create multi-level hierarchy (5+ levels)
- [ ] Move role to different parent
- [ ] Delete role with children (cascade)
- [ ] Assign user to hierarchical role
- [ ] Verify TeamMembership auto-creation
- [ ] Check permission inheritance
- [ ] Test circular reference prevention
- [ ] Load test with 100+ roles
- [ ] Frontend tree rendering
- [ ] Drag-and-drop reorganization

---

## Benefits

✅ **Dynamic Role Creation** - Add organizational positions on the fly
✅ **Clear Hierarchy** - Visual tree structure
✅ **Auto Team Management** - Teams determined by hierarchy
✅ **Permission Inheritance** - Simplified permission management
✅ **Scalable** - Supports complex organizational structures
✅ **Multi-College** - Each college has independent hierarchy

---

## Next Steps

1. Review and approve this implementation plan
2. Create database migration
3. Implement backend APIs
4. Create frontend components
5. Test with sample data
6. Deploy to staging
7. Train users on new system
