# College Store Feature - Backend Documentation

## Overview

This document describes the backend implementation of the **College Store** feature, which allows colleges to manage their own stores independently from the Central Store.

---

## Database Changes

### New Model: `CollegeStore`

**Table:** `college_store`

**Fields:**

| Field           | Type           | Constraints             | Description           |
| --------------- | -------------- | ----------------------- | --------------------- |
| `id`            | Integer        | Primary Key             | Auto-generated ID     |
| `college_id`    | ForeignKey     | NOT NULL, FK to College | College reference     |
| `name`          | CharField(200) | NOT NULL                | Store name            |
| `code`          | CharField(20)  | NOT NULL                | Store code            |
| `address_line1` | CharField(300) | NULL                    | Address line 1        |
| `address_line2` | CharField(300) | NULL                    | Address line 2        |
| `city`          | CharField(100) | NULL                    | City                  |
| `state`         | CharField(100) | NULL                    | State                 |
| `pincode`       | CharField(10)  | NULL                    | Postal code           |
| `manager_id`    | ForeignKey     | NULL, FK to User        | Store manager         |
| `contact_phone` | CharField(20)  | NULL                    | Contact phone         |
| `contact_email` | EmailField     | NULL                    | Contact email         |
| `is_active`     | Boolean        | Default: True           | Active status         |
| `created_at`    | DateTime       | Auto                    | Creation timestamp    |
| `updated_at`    | DateTime       | Auto                    | Last update timestamp |

**Constraints:**

- `UNIQUE (college_id, code)` - Code must be unique within a college
- Index on `(college_id, is_active)`
- Index on `code`

**Relationships:**

- `college` → `College` (CASCADE)
- `manager` → `User` (SET_NULL)

---

## API Endpoints

### Base URL: `/api/v1/store/college-stores/`

### 1. List College Stores (NEW)

```
GET /api/v1/store/college-stores/
```

**Permissions:** `CanManageCollegeStore`

- Super Admin: See all stores
- College Admin: See only their college's stores
- Central Store Manager: See all stores

**Query Parameters:**

- `is_active` (boolean) - Filter by active status
- `college` (integer) - Filter by college ID
- `search` (string) - Search in name, code, city
- `ordering` (string) - Sort by: name, code, created_at

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "college": 5,
    "college_name": "Engineering College",
    "name": "Main Store",
    "code": "ENG-MAIN",
    "address_line1": "Building A",
    "address_line2": null,
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "manager": 10,
    "manager_name": "John Doe",
    "contact_phone": "9876543210",
    "contact_email": "store@college.edu",
    "is_active": true,
    "created_at": "2026-01-07T10:00:00Z",
    "updated_at": "2026-01-07T10:00:00Z"
  }
]
```

---

### 2. Create College Store (NEW)

```
POST /api/v1/store/college-stores/
```

**Permissions:** `CanManageCollegeStore`

**Request Body:**

```json
{
  "college": 5,
  "name": "Science Department Store",
  "code": "SCI-DEPT",
  "address_line1": "Science Block",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "manager": 12,
  "contact_phone": "9876543210",
  "contact_email": "science@college.edu"
}
```

**Validation:**

- `college` - Required, must exist
- `name` - Required, max 200 chars
- `code` - Required, max 20 chars, unique per college
- `contact_email` - Must be valid email format

**Response:** `201 Created`

```json
{
  "id": 2,
  "college": 5,
  "name": "Science Department Store",
  "code": "SCI-DEPT",
  ...
}
```

**Errors:**

- `400 Bad Request` - Validation errors
  ```json
  {
    "code": ["Store with this College and Code already exists."]
  }
  ```
- `403 Forbidden` - Permission denied

---

### 3. Retrieve College Store (NEW)

```
GET /api/v1/store/college-stores/{id}/
```

**Permissions:** `CanManageCollegeStore`

**Response:** `200 OK`

```json
{
  "id": 1,
  "college": 5,
  "name": "Main Store",
  ...
}
```

---

### 4. Update College Store (NEW)

```
PUT /api/v1/store/college-stores/{id}/
PATCH /api/v1/store/college-stores/{id}/
```

**Permissions:** `CanManageCollegeStore`

**Request Body:** Same as create (PATCH allows partial updates)

**Response:** `200 OK`

**Errors:**

- `400 Bad Request` - Validation errors
- `403 Forbidden` - Permission denied
- `404 Not Found` - Store not found

---

### 5. Delete College Store (NEW)

```
DELETE /api/v1/store/college-stores/{id}/
```

**Permissions:** `CanManageCollegeStore`

**Response:** `204 No Content`

**Note:** This is a soft delete (sets `is_active=False`)

---

## Permissions

### New Permission Class: `CanManageCollegeStore`

**File:** `apps/store/permissions.py`

**Logic:**

```python
def has_permission(self, request, view):
    # Super admin - full access
    if user.is_superuser:
        return True

    # Central store manager - full access
    if user.user_type == 'central_manager':
        return True

    # College admin - can manage stores for their college only
    if user.user_type == 'college_admin' and hasattr(user, 'college_id'):
        return True

    return False
```

**Applied to:**

- `CollegeStoreViewSet` - All actions

---

## Code Files Modified

### 1. `apps/store/models.py`

- **Added:** `CollegeStore` model (after `CentralStore`)

### 2. `apps/store/serializers.py`

- **Added:** `CollegeStoreSerializer`
- **Added:** `CollegeStoreListSerializer`
- **Updated:** Import list to include `CollegeStore`

### 3. `apps/store/views.py`

- **Added:** `CollegeStoreViewSet`
- **Updated:** Import lists

### 4. `apps/store/urls.py`

- **Added:** Route `college-stores` → `CollegeStoreViewSet`

### 5. `apps/store/permissions.py`

- **Added:** `CanManageCollegeStore` permission class

---

## Migration Required

Run the following commands to apply database changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

**Expected Migration:**

- Creates `college_store` table
- Adds indexes and constraints

---

## Testing

### Manual Testing

**1. Super Admin:**

```bash
# Create store for any college
curl -X POST http://localhost:8000/api/v1/store/college-stores/ \
  -H "Authorization: Bearer {super_admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "college": 1,
    "name": "Test Store",
    "code": "TEST-01"
  }'
```

**2. College Admin:**

```bash
# Create store for their college only
curl -X POST http://localhost:8000/api/v1/store/college-stores/ \
  -H "Authorization: Bearer {college_admin_token}" \
  -H "X-College-ID: 5" \
  -H "Content-Type: application/json" \
  -d '{
    "college": 5,
    "name": "College Store",
    "code": "CLG-01"
  }'
```

**3. Regular User (Should Fail):**

```bash
# Should return 403 Forbidden
curl -X POST http://localhost:8000/api/v1/store/college-stores/ \
  -H "Authorization: Bearer {regular_user_token}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Test Cases

- [ ] Super admin can create stores for any college
- [ ] College admin can create stores only for their college
- [ ] Central store manager can create stores for any college
- [ ] Regular users get 403 Forbidden
- [ ] Code uniqueness is enforced per college
- [ ] Soft delete works (is_active=False)
- [ ] College scoping works correctly
- [ ] Search and filters work
- [ ] Serializers return correct data

---

## Future Enhancements

### Potential Features:

1. **Inventory Management** - Link `StoreItem` to `CollegeStore`
2. **Transfer Between Stores** - Allow inter-college store transfers
3. **Store Reports** - Analytics for college store performance
4. **Store Hierarchy** - Support for sub-stores within a college

---

## Rollback Plan

If issues arise, rollback using:

```bash
# Rollback migration
python manage.py migrate store <previous_migration_number>

# Remove routes from urls.py
# Comment out CollegeStoreViewSet registration
```

---

## Support

For questions or issues, contact the backend development team.
