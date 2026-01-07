# College Store Feature - Frontend Developer Guide

## Overview

A new **College Store** feature has been added to allow colleges to manage their own stores separately from the Central Store. This document outlines the changes needed in the frontend.

---

## New API Endpoints

### Base URL

```
/api/v1/store/college-stores/
```

### Available Endpoints

#### 1. **List College Stores** (NEW)

```http
GET /api/v1/store/college-stores/
```

**Response:**

```json
[
  {
    "id": 1,
    "college": 5,
    "college_name": "Engineering College",
    "name": "Main Store",
    "code": "ENG-MAIN",
    "address_line1": "Building A, Floor 2",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001",
    "manager": 10,
    "manager_name": "John Doe",
    "contact_phone": "9876543210",
    "contact_email": "store@college.edu",
    "is_active": true,
    "created_at": "2026-01-07T10:00:00Z"
  }
]
```

**Filters:**

- `?is_active=true` - Filter by active status
- `?college=5` - Filter by college ID
- `?search=Main` - Search by name, code, or city

---

#### 2. **Create College Store** (NEW)

```http
POST /api/v1/store/college-stores/
```

**Request Body:**

```json
{
  "college": 5,
  "name": "Science Department Store",
  "code": "SCI-DEPT",
  "address_line1": "Science Block, Room 101",
  "address_line2": "Near Lab Area",
  "city": "Mumbai",
  "state": "Maharashtra",
  "pincode": "400001",
  "manager": 12,
  "contact_phone": "9876543210",
  "contact_email": "science.store@college.edu"
}
```

**Required Fields:**

- `college` (integer)
- `name` (string)
- `code` (string, unique per college)

**Optional Fields:**

- `address_line1`, `address_line2`, `city`, `state`, `pincode`
- `manager` (user ID)
- `contact_phone`, `contact_email`

**Response:** Same as list item above

---

#### 3. **Get College Store Details** (NEW)

```http
GET /api/v1/store/college-stores/{id}/
```

**Response:** Same as list item

---

#### 4. **Update College Store** (NEW)

```http
PUT /api/v1/store/college-stores/{id}/
PATCH /api/v1/store/college-stores/{id}/
```

**Request Body:** Same as create (PATCH allows partial updates)

---

#### 5. **Delete College Store** (NEW)

```http
DELETE /api/v1/store/college-stores/{id}/
```

**Response:** `204 No Content`

---

## Permissions

### Who Can Create/Manage College Stores?

Only the following user types can create or manage college stores:

1. **Super Admin** (`is_superuser=true`)
2. **College Admin** (`user_type='college_admin'`) - Can only manage stores for their own college
3. **Central Store Manager** (`user_type='central_manager'`)

### Frontend Permission Checks

Before showing the "Create Store" button, check:

```javascript
const canManageCollegeStore =
  user.is_superuser ||
  user.user_type === "college_admin" ||
  user.user_type === "central_manager";
```

---

## UI Changes Required

### 1. **New Menu Item**

Add a new menu item under the Store module:

- **Label:** "College Stores"
- **Route:** `/store/college-stores`
- **Icon:** Store/Building icon
- **Visibility:** Show only to users with `canManageCollegeStore` permission

### 2. **College Stores List Page**

Create a new page to display all college stores:

**Features:**

- Table/Grid view with columns:
  - College Name
  - Store Name
  - Store Code
  - Manager Name
  - Contact Phone
  - Status (Active/Inactive)
  - Actions (Edit, Delete)
- Search bar (searches name, code, city)
- Filter by:
  - College (dropdown)
  - Active status (toggle)
- "Create New Store" button (top-right)

**College Admin Behavior:**

- Automatically filter to show only their college's stores
- Hide college selection in create/edit forms

### 3. **Create/Edit College Store Form**

**Form Fields:**

**Basic Information:**

- College\* (dropdown - auto-select for college admins)
- Store Name\* (text input)
- Store Code\* (text input, unique per college)

**Address:**

- Address Line 1 (text input)
- Address Line 2 (text input)
- City (text input)
- State (dropdown/text input)
- Pincode (text input)

**Contact Details:**

- Manager (user dropdown - filter by college)
- Contact Phone (text input with validation)
- Contact Email (email input)

**Validation:**

- Required fields marked with \*
- Code must be unique within the college
- Email format validation
- Phone number format validation

### 4. **Integration with Existing Features**

**Store Items:**

- When creating/editing store items, add option to link to College Store
- Update `StoreItem` forms to include `college_store` field (if applicable)

**Indents:**

- College stores can raise indents to Central Store
- Update indent creation to allow selection of requesting college store

---

## Example Frontend Code

### Fetch College Stores

```javascript
const fetchCollegeStores = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/v1/store/college-stores/?${params}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "X-College-ID": collegeId,
    },
  });
  return response.json();
};
```

### Create College Store

```javascript
const createCollegeStore = async (data) => {
  const response = await fetch("/api/v1/store/college-stores/", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "X-College-ID": collegeId,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create store");
  }

  return response.json();
};
```

---

## Error Handling

### Common Errors

**403 Forbidden:**

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Action:** Show error message, redirect to dashboard

**400 Bad Request:**

```json
{
  "code": ["Store with this College and Code already exists."]
}
```

**Action:** Show validation error on form field

---

## Testing Checklist

- [ ] Super admin can create stores for any college
- [ ] College admin can only create stores for their college
- [ ] Central store manager can create stores for any college
- [ ] Regular users cannot access college store management
- [ ] Store code uniqueness is enforced per college
- [ ] Form validation works correctly
- [ ] Search and filters work as expected
- [ ] Edit and delete operations work
- [ ] Proper error messages are displayed

---

## Questions?

Contact the backend team for any clarifications on the API behavior or permissions.
