# Changes OH

- Restricted org tree endpoint to superadmin users only.
- Synced DynamicRole permission updates into core Permission records.
- Allowed hierarchy roles (including custom codes) to drive permission lookups.
- Expanded superadmin check to include user_type super_admin.
- Built a virtual CEO -> College -> Role tree from existing College/DynamicRole data when no org nodes exist.
- Virtual tree now pulls college-scoped roles from apps.accounts.models.Role (parent-based) when available, so teachers/students display per college.
- Tree now hides empty positions and includes members_count per role using UserRole/HierarchyUserRole allocations.
- Tree now falls back to showing role nodes even when allocations are missing, using user_type counts if available.
- Added user_type-based fallback nodes (with counts) when no roles exist, including global user_type nodes.
