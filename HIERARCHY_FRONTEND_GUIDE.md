# Hierarchical Role System - Frontend Integration Guide

This document describes the backend APIs and data contract for the organizational
hierarchy (role tree) feature, along with expected frontend behaviors.

---

## 1) Overview

The backend now supports:
- Hierarchical roles with parent-child relationships
- A role tree API for rendering an org chart
- Dynamic child role creation
- Hierarchy path and descendants queries
- Automatic team membership linkage based on hierarchy

Frontend should render the hierarchy under the Admin area as a tree view and
use the endpoints below for CRUD and team lookup.

---

## 2) Core Endpoints

Base path (from accounts app router):
```
/api/v1/accounts/roles/
```

### A) Get Role Tree
```
GET /api/v1/accounts/roles/tree/
```

Response:
```json
{
  "tree": [
    {
      "id": "uuid-1",
      "name": "Principal",
      "code": "PRINCIPAL",
      "description": "Top level role",
      "parent": null,
      "parent_name": null,
      "level": 0,
      "is_organizational_position": true,
      "children": [
        {
          "id": "uuid-2",
          "name": "HOD",
          "code": "HOD",
          "description": "",
          "parent": "uuid-1",
          "parent_name": "Principal",
          "level": 1,
          "is_organizational_position": true,
          "children": []
        }
      ]
    }
  ]
}
```

Notes:
- The tree is built from `parent` relationships. Create/update roles with the correct `parent` to form the structure.
- Sibling ordering is controlled by `display_order`, then `name`.
- Multiple top-level roots are supported (roles with `parent = null`).

### B) Add Child Role
```
POST /api/v1/accounts/roles/{role_id}/add_child/
```

Request:
```json
{
  "name": "Class Coordinator",
  "code": "CLASS_COORD",
  "description": "Coordinates a class",
  "permissions": {},
  "is_organizational_position": true,
  "display_order": 0
}
```

Response (RoleSerializer):
```json
{
  "id": "uuid-3",
  "college": "college-uuid",
  "college_name": "KUMSS",
  "name": "Class Coordinator",
  "code": "CLASS_COORD",
  "description": "Coordinates a class",
  "permissions": {},
  "parent": "uuid-2",
  "is_organizational_position": true,
  "level": 2,
  "display_order": 0,
  "is_active": true,
  "created_by_name": "Admin User",
  "updated_by_name": "Admin User",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### C) Get Team Members Under a Role
```
GET /api/v1/accounts/roles/{role_id}/team_members/
```

Response:
```json
{
  "role": "HOD",
  "team_members": [
    {
      "user_id": "user-uuid-1",
      "name": "John Doe",
      "role": "Teacher",
      "level": 2
    }
  ],
  "total": 1
}
```

Note:
- Use this to show the people under a node (if your UI needs names inside each box).

### D) Get Hierarchy Path
```
GET /api/v1/accounts/roles/{role_id}/hierarchy_path/
```

Response:
```json
{
  "path": [
    { "id": "uuid-1", "name": "Principal", "level": 0 },
    { "id": "uuid-2", "name": "HOD", "level": 1 },
    { "id": "uuid-3", "name": "Teacher", "level": 2 }
  ]
}
```

### E) Get Descendants
```
GET /api/v1/accounts/roles/{role_id}/descendants/
```

Response:
```json
{
  "role": "Principal",
  "descendants": [
    {
      "id": "uuid-2",
      "name": "HOD",
      "code": "HOD",
      "level": 1,
      "parent": "uuid-1"
    }
  ],
  "total": 1
}
```

---

## 3) Role Fields (Backend Model)

Each Role includes:
- `parent` (self FK, nullable)
- `level` (integer, 0 = root)
- `is_organizational_position` (boolean)
- `permissions` (JSON)
- `display_order` (integer)

`level` is auto-computed based on parent.

---

## 4) UI/UX Expectations

Suggested Admin page:
```
Admin > Roles > Hierarchy
```

Recommended features:
- Tree view (expand/collapse)
- Add child role from a node
- Edit role details
- Team view panel showing team members
- Breadcrumb using hierarchy_path

---

## 5) How To Build A Complex Org Tree (Frontend Guidance)

To reproduce a diagram like the screenshot:

1) Create a root role (e.g., CEO) with `parent = null`.
2) For each box under the root, create a child role using `add_child`.
3) For deeper levels, keep adding children under the correct parent.
4) Set `display_order` to control sibling order left-to-right.
5) If you need multiple independent branches (e.g., a separate college unit),
   create multiple root roles.

Minimal payload to create a node:
```json
{
  "name": "Viceprincipal",
  "code": "VICE_PRINCIPAL",
  "description": "",
  "permissions": {},
  "is_organizational_position": true,
  "display_order": 10
}
```

Notes:
- `code` must be unique per college and is forced to uppercase.
- Use consistent `display_order` spacing (e.g., 10, 20, 30) to make inserts easy.

---

## 6) Team & Permission Linking

Team is auto-derived from hierarchy:
- When a user gets assigned a role, the system creates TeamMembership entries
  for all ancestors/descendants in the hierarchy.
- This is used by permission scopes (team scope).

Frontend does NOT need to manually assign team members; it is automatic.

---

## 7) Headers and Auth

All endpoints require authentication. For college-scoped access:
- Header: `X-College-ID: <college-id>`
- Superadmins may omit or use `all`.

---

## 8) Error Handling Notes

Common backend validations:
- Role code must be unique per college
- Circular parent relationships are not allowed
- Role cannot be its own parent

Expected error response:
```json
{
  "detail": "Role hierarchy cannot be circular."
}
```

---

## 9) Quick Frontend Data Flow

```
GET /roles/tree/ -> render tree
Click node -> GET /roles/{id}/team_members/ -> show team panel
Click add child -> POST /roles/{id}/add_child/ -> update tree
```

---

## 10) Notes for Frontend Developer

This hierarchy is used only under Admin.
The rest of the application can continue to use roles/permissions as-is.
If needed, we can add drag-and-drop reorder later.

For large trees:
- Fetch `/roles/tree/` once, then lazy-load team members per node.
- If you need a "show people inside each node" view, either:
  - call `/team_members/` on node select, or
  - request a backend enhancement to embed a compact user list in the tree payload.
