# Changes OH

- Restricted org tree endpoint to superadmin users only.
- Synced DynamicRole permission updates into core Permission records.
- Allowed hierarchy roles (including custom codes) to drive permission lookups.
- Expanded superadmin check to include user_type super_admin.
- Built a virtual CEO -> College -> Role tree from existing College/DynamicRole data when no org nodes exist.
