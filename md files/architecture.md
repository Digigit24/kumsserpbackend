# KUMSS Architecture

## Stack & Modules
- Django + Django REST Framework with drf-spectacular for OpenAPI docs.
- Core app models (College, AcademicYear, AcademicSession, Holiday, Weekend, SystemSetting, NotificationSetting, ActivityLog) inherit shared audit/timestamp bases and a college-aware `CollegeManager` by default.
- Thread-local utilities in `apps/core/utils.py` hold per-request college context and request metadata (no tenant IDs remain).

## College-Scoped Model
- Tenancy is scoped by college: frontend sends `X-College-ID` (legacy fallback `X-Tenant-ID`) containing the college primary key.
- `CollegeMiddleware` resolves that header to a `College` (using `College.objects.all_colleges()` to bypass scoping), then sets thread-local `college_id`. The request object is also stored for later audit capture.
- `CollegeScopedMixin` (used by all API ViewSets) enforces presence of a valid college header, and all ViewSets inherit college-aware filtering + save hooks (`CollegeScopedModelViewSet` / `CollegeScopedReadOnlyModelViewSet`). Querysets are filtered by `college_id` when the model has a `college` FK, or by PK for the College model itself.
- `CollegeManager` defaults every model query to `for_current_college()`, applying college filters from thread-local context. Use `Model.objects.all_colleges()` for admin/system operations that need to bypass scoping.
- `CollegeScopedModel` base ensures `college_id` is auto-populated from the current request context on save when a model carries a `college` FK to avoid cross-college writes.

## Cross-Cutting Behaviors
- Signals (`apps/core/signals.py`): College creation seeds NotificationSetting + default Weekend entries; AcademicYear enforces a single `is_current` per college; ActivityLog captures client IP/user agent from the stored request.
- Audit: Save hooks in the college mixin stamp `created_by`/`updated_by` when serializer fields exist. Models inherit timestamp + audit fields and support soft-delete (`is_active`).
- Activity logging: `ActivityLog` uses the same college manager and is tied to the `college` FK for isolation.

## Adding New College-Aware Features
- Use `CollegeScopedModel` (or `CollegeManager` on non-abstract bases) for new models to inherit college scoping.
- Derive APIs from `CollegeScopedModelViewSet`/`CollegeScopedReadOnlyModelViewSet` to get automatic filtering and audit stamping. Avoid manual queryset filtering for isolation.
- For system-wide/maintenance code paths (scripts, admin actions), either set thread-local college IDs via `apps.core.utils.set_current_college_id` or call `.all_colleges()` on the manager to bypass scoping deliberately.

## Request Lifecycle (happy path)
1. Client request includes `X-College-ID: <college_id>` (legacy `X-Tenant-ID` still accepted).
2. `CollegeMiddleware` maps it to college context and stores the request.
3. ViewSet `initial` enforces the header; queryset generation is college-filtered.
4. Serializer `save()` is called with enforced `college_id` (when applicable) plus audit fields.
5. Response cleanup clears thread-local college/request context.
