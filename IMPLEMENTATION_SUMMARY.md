# Hierarchical Role System - Implementation Summary

## How We Will Implement This

### 1. Database Level
- **Add 3 fields to Role model**:
  - `parent` (self-referencing FK) - links roles in hierarchy
  - `is_organizational_position` (boolean) - marks as org position
  - `level` (integer) - hierarchy depth (auto-calculated)

### 2. Backend APIs (5 New Endpoints)
- `GET /roles/tree/` - Full hierarchy tree
- `POST /roles/{id}/add_child/` - Add child role dynamically
- `GET /roles/{id}/team_members/` - Get team members (auto from hierarchy)
- `GET /roles/{id}/hierarchy_path/` - Get ancestors chain
- `GET /roles/{id}/descendants/` - Get all children

### 3. Auto Team Linking
- When user assigned to role → automatically create TeamMembership
- Team = all users in descendant roles
- Example: Assign user as HOD → auto-links to all teachers/coordinators under them

### 4. Permission Linking
- Already linked via existing Permission model
- Will add inheritance: child roles inherit parent permissions
- Child can restrict (never expand) parent permissions

---

## Backend Changes

### Files Modified
1. **`apps/accounts/models.py`**
   - Add `parent`, `is_organizational_position`, `level` to Role
   - Add methods: `get_descendants()`, `get_ancestors()`, `get_team_members()`

2. **`apps/accounts/views.py`**
   - Add 5 new action endpoints to RoleViewSet

3. **`apps/accounts/serializers.py`**
   - Create `RoleTreeSerializer` with nested children

4. **`apps/core/signals.py`** (NEW)
   - Auto-create TeamMembership on UserRole assignment

### New Migration
- `apps/accounts/migrations/XXXX_add_role_hierarchy.py`

---

## Frontend Changes

### New Admin Page: `/admin/roles/hierarchy`

**Features**:
1. **Tree View** - Visual org chart
2. **Add Role** - Click parent → add child
3. **Edit Role** - Inline editing
4. **Drag & Drop** - Reorganize hierarchy
5. **Team View** - Click role → see team members
6. **Permission Editor** - Manage permissions per role

### New Components
- `RoleTree.jsx` - Tree visualization
- `RoleNode.jsx` - Each role in tree
- `RoleEditor.jsx` - Edit modal
- `AddRoleModal.jsx` - Add role modal
- `TeamMemberList.jsx` - Team members list
- `PermissionMatrix.jsx` - Permission grid

### Data Flow
```
Frontend → GET /roles/tree/ → Render tree
Click "Add Child" → POST /roles/{id}/add_child/ → Update tree
Click role → GET /roles/{id}/team_members/ → Show team
```

---

## What Changes After Implementation

### Backend
✅ Roles have parent-child relationships
✅ Can create roles dynamically via API
✅ Teams auto-populated based on hierarchy
✅ Permissions inherit from parent roles
✅ Query role trees efficiently
✅ Get team members for any role

### Frontend (Admin)
✅ Visual role hierarchy tree
✅ Click-to-add child roles
✅ Drag-and-drop reorganization
✅ See team members per role
✅ Edit permissions with inheritance
✅ Breadcrumb showing role path

### User Experience
✅ **Admin**: Manage org structure visually
✅ **Users**: Assigned to positions (not abstract roles)
✅ **Teams**: Auto-determined by hierarchy
✅ **Permissions**: Inherited from org position

---

## Example Usage

### Before (Current System)
```
1. Create Role "HOD"
2. Create Role "Teacher"
3. Manually create TeamMembership(HOD → Teacher)
4. Assign permissions separately
```

### After (New System)
```
1. Create Role "Principal" (root)
2. Click Principal → Add child "HOD"
3. Click HOD → Add child "Class Coordinator"
4. Click Class Coordinator → Add child "Teacher"
5. Assign user to "Teacher" role
   → Auto-creates TeamMembership with Class Coordinator, HOD, Principal
   → Auto-inherits permissions from parent roles
```

---

## Implementation Steps

1. ✅ **Review Documentation** (this file)
2. ⏳ **Create Migration** - Add hierarchy fields to Role
3. ⏳ **Update Models** - Add methods for tree operations
4. ⏳ **Create APIs** - 5 new endpoints
5. ⏳ **Add Signals** - Auto TeamMembership creation
6. ⏳ **Build Frontend** - Role hierarchy page
7. ⏳ **Test** - Verify hierarchy, teams, permissions
8. ⏳ **Deploy** - Production release

---

## Technical Details

### Database Schema Change
```sql
ALTER TABLE role ADD COLUMN parent_id UUID REFERENCES role(id);
ALTER TABLE role ADD COLUMN is_organizational_position BOOLEAN DEFAULT TRUE;
ALTER TABLE role ADD COLUMN level INTEGER DEFAULT 0;
CREATE INDEX idx_role_parent ON role(parent_id);
```

### API Response Example
```json
{
  "tree": [
    {
      "id": "uuid-1",
      "name": "Principal",
      "level": 0,
      "children": [
        {
          "id": "uuid-2",
          "name": "HOD",
          "level": 1,
          "children": [
            {
              "id": "uuid-3",
              "name": "Teacher",
              "level": 2,
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

### Frontend Code Example
```javascript
// Fetch and display tree
const tree = await axios.get('/api/v1/accounts/roles/tree/');
<RoleTree data={tree.data.tree} />

// Add child role
await axios.post(`/api/v1/accounts/roles/${parentId}/add_child/`, {
  name: "Department Head",
  code: "DEPT_HEAD"
});
```

---

## Summary

**Current**: Flat roles, manual teams, separate permissions

**After Implementation**: Hierarchical org chart, auto teams, inherited permissions

**Key Benefit**: Org structure defines everything - roles, teams, permissions flow from hierarchy
