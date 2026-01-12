# Organizational Hierarchy Overview

The hierarchy feature adds a tree-based org structure using `OrganizationNode` (MPTT), where each node can link to a user, college, and a dynamic role. `DynamicRole` and `HierarchyPermission` define flexible permissions; `RolePermission` maps roles to permissions with scope, and `HierarchyUserRole` assigns roles to users. Teams are modeled with `Team` and `HierarchyTeamMember` to group users around nodes.

API endpoints under `organization/` provide CRUD for nodes, roles, permissions, user-role assignments, and teams, plus a cached tree endpoint. Serializers expose nested role and user details, and count helpers. Permissions are checked via `PermissionChecker`, which caches user permissions in Redis. `RoleManagementService` enforces role assignment rules by permission and role level. `TeamAutoAssignmentService` auto-creates teams for key nodes and assigns teachers/students based on hierarchy.

Signals keep caches in sync and auto-create teams on node creation. A management command seeds default permissions. Admin uses MPTT to manage the tree.
