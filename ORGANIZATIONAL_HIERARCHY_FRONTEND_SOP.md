# Frontend SOP: Organizational Hierarchy (OH)

- Use org APIs from `apps.core.hierarchy_views` (router prefix `/api/v1/core/organization/`).
- Required header for scoped data: `X-College-Id`.
- Tree view: `GET organization/nodes/tree/` returns nested nodes (cached 5 min); use this for main hierarchy UI.
- Node CRUD: `organization/nodes/` (create/update clears cache).
- Roles: `organization/roles/`; update permissions via `PATCH organization/roles/{id}/update_permissions/` with `{add:[permId], remove:[permId]}`.
- Permissions list: `organization/hierarchy-permissions/` and `.../by_category/` for grouped UI.
- User role assignment: `organization/user-roles/assign/` and `/revoke/`.
- Teams: `organization/teams/`; members via `.../{id}/members/` and add via `.../{id}/add_member/`.
- Models to align UI fields: `OrganizationNode`, `DynamicRole`, `HierarchyPermission`, `RolePermission`, `HierarchyUserRole`, `Team`, `HierarchyTeamMember` in `apps/core/models.py`.
- Auto behavior: teams are auto-created for nodes (principal/hod/teacher) and permissions are cached per user (Redis).
- Existing app-level permissions still use `apps/core/permissions/registry.py` + `scope_resolver.py`; OH permissions manage org structure only.
