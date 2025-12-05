# 📋 KUMSS ERP - Project Constitution & Architectural Rules

## 1. Project Overview & Architecture
* **System Type:** Monolithic Django Application with Modular App Structure.
* **Multi-Tenancy:** **Database-per-Tenant** architecture.
    * **Tenant Isolation:** Strict isolation at the database level.
    * **Identification:** Tenant is identified via HTTP Header `X-Tenant-ID`.
    * **Routing:** Dynamic database routing based on the tenant context.
* **Folder Structure:**
    * All Django apps reside in `apps/` (e.g., `apps/core`, `apps/students`).
    * Settings are split in `kumss_erp/settings/` (`base.py`, `dev.py`, `prod.py`).

## 2. Technology Stack
* **Backend:** Python 3.11+, Django 5.0+, Django REST Framework (DRF).
* **Database:** PostgreSQL 16+ (Neon Cloud).
* **Async/Cache:** Redis 7+, Celery 5+.
* **Storage:** AWS S3 / MinIO.
* **API Docs:** drf-spectacular (OpenAPI 3.0).

## 3. 🚨 CRITICAL: Multi-Tenancy Rules
1.  **Inheritance:** ALL business models (Students, Fees, Exams) **MUST** inherit from `TenantModel`.
    * *Exception:* Global system configs or Users (if shared) may inherit from `AuditModel` only.
2.  **Context Context:** The `tenant_id` must be extracted from the request header (`X-Tenant-ID`) via Middleware and stored in **Thread Local Storage**.
3.  **Database Routing:**
    * Read/Write operations must route to `tenant_{tenant_id}` based on the thread-local context.
    * If no tenant ID is present, route to `default` (system DB).

## 4. Coding Standards & Conventions

### Model Design
* **Abstract Base Classes (in `apps.core.models`):**
    * `TimeStampedModel`: Adds `created_at`, `updated_at`.
    * `AuditModel`: Inherits `TimeStampedModel`. Adds `created_by`, `updated_by`, `is_active` (Soft Delete).
    * `TenantModel`: Inherits `AuditModel`. Adds `tenant_id` (Indexed).
* **Fields:**
    * Date/Time: Use `DateTimeField` for logs, `DateField` for DOB/Events.
    * JSON: Use `JSONField` for flexible settings (see specific schemas below).
    * Money: Use `DecimalField` (never Float).
* **Naming:**
    * Classes: `PascalCase` (e.g., `AcademicYear`).
    * Variables/Fields: `snake_case` (e.g., `is_current`).
    * Related Names: Pluralized (e.g., `college.students`).

### API Design (DRF)
* **Response Format:** ALWAYS use this standard wrapper:
    ```json
    {
      "success": true,
      "message": "Operation successful",
      "data": { ... },
      "errors": null,
      "meta": { "page": 1, "total": 100 }
    }
    ```
* **Versioning:** URL namespace `/api/v1/...`.
* **Statelessness:** No session auth for APIs. Use JWT (Access + Refresh).

## 5. 📦 Core App Domain Logic (The Truth)

### Models & Logic
**1. College**
* **Parent:** `TenantModel` (technically usually stored in shared DB, but defined with tenant context).
* **Settings JSON Schema:**
    * `academic`: `{ "attendance_mandatory_percentage": int, "grading_system": str }`
    * `fees`: `{ "late_fee_percentage": int, "installment_allowed": bool }`
    * `theme`: `{ "primary_font": str, "logo_url": str }`

**2. AcademicYear**
* **Constraint:** Pair `(tenant_id, year)` must be unique.
* **Logic (Signal):** If `is_current=True` is saved, ALL other years for that `tenant_id` must be set to `is_current=False` automatically.

**3. AcademicSession**
* **Constraint:** Pair `(tenant_id, college, academic_year, semester)` must be unique.

**4. Holiday & Weekend**
* **Holiday Types:** `['national', 'festival', 'college', 'exam']`.
* **Weekend Days:** 0=Monday ... 6=Sunday.

**5. ActivityLog**
* **Trigger:** **Pre-Save Signal** must populate:
    * `ip_address`: From request context (handle load balancers).
    * `user_agent`: From request headers.
* **Actions:** `['create', 'read', 'update', 'delete', 'login', 'logout', 'export']`.

**6. NotificationSetting**
* **Trigger:** Auto-created when a `College` is created.
* **JSON Schema:**
    * `channels`: `{ "sms": bool, "email": bool, "whatsapp": bool }`
    * `schedules`: `{ "fee_reminder_time": "09:00" }`

### Automation (Signals)
1.  **College Created:**
    * -> Create `NotificationSetting`.
    * -> Create `Weekend` entries (defaults: Sat & Sun).
2.  **Audit Logging:**
    * Middleware captures `request` and `tenant_id` -> stores in Thread Local.
    * `AuditModel` uses this to populate `created_by`/`updated_by`.

## 6. Development Workflow Rules
1.  **Zero-Logic Views:** Keep Views thin. Move business logic to **Serializers** or **Service Layers**.
2.  **No Hardcoding:** Use `TextChoices` or `IntegerChoices` for enums (Holiday Types, Roles).
3.  **Soft Deletes:** Never `DELETE` from DB. Set `is_active=False`. Filter managers to exclude inactive by default.
4.  **Security:** Always validate `tenant_id` availability before performing Write operations.