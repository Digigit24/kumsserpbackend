# Super Admin Timetable API Documentation

This documentation details the API endpoints for managing timetables, specifically tailored for Super Admin access to view and manage timetables across all colleges and classes.

**Base URL**: `/api/v1/academic/timetable/`

## Authentication

- **Headers**:
  - `Authorization`: `Bearer <access_token>`
  - `X-College-ID`: `all` (Optional for Super Admin to explicitly request global data, though standard superuser accounts may access all data by default).

## Endpoints

### 1. List All Timetables

Retrieve a paginated list of timetable entries. Super Admins can see entries from all colleges.

**Endpoint**: `GET /api/v1/academic/timetable/`

**Query Parameters (Filtering)**:

- `section`: (Integer) Filter by section ID.
- `day_of_week`: (Integer) Filter by day of week (0=Monday, 6=Sunday).
- `class_time`: (Integer) Filter by class time slot ID.
- `classroom`: (Integer) Filter by classroom ID.
- `is_active`: (Boolean) `true` or `false`.
- `ordering`: (String) Filter by field, e.g., `day_of_week`, `class_time__period_number`.

**Response (200 OK)**:

```json
[
  {
    "id": 1,
    "class_obj": 101,
    "class_name": "CS-A Sem 1",
    "section": 201,
    "section_name": "Section A",
    "subject_assignment": 305,
    "subject_name": "Data Structures",
    "teacher_name": "Dr. John Doe",
    "day_of_week": 0,
    "class_time": 15,
    "time_slot": "Period 1 (09:00:00 - 10:00:00)",
    "classroom": 50,
    "classroom_name": "Room 101",
    "effective_from": "2024-01-01",
    "is_active": true
  },
  {
    "id": 2,
    "class_obj": 102,
    "class_name": "CS-B Sem 1",
    "section": 202,
    "section_name": "Section B",
    "subject_assignment": 310,
    "subject_name": "Algorithms",
    "teacher_name": "Prof. Jane Smith",
    "day_of_week": 0,
    "class_time": 16,
    "time_slot": "Period 2 (10:00:00 - 11:00:00)",
    "classroom": 51,
    "classroom_name": "Room 102",
    "effective_from": "2024-01-01",
    "is_active": true
  }
]
```

---

### 2. Create Timetable Entry

Create a new timetable entry.

**Endpoint**: `POST /api/v1/academic/timetable/`

**Request Payload**:

```json
{
  "class_obj": 101,
  "section": 201,
  "subject_assignment": 305,
  "day_of_week": 0,
  "class_time": 15,
  "classroom": 50,
  "effective_from": "2024-01-01",
  "is_active": true
}
```

| Field                | Type    | Required | Description                                             |
| -------------------- | ------- | -------- | ------------------------------------------------------- |
| `class_obj`          | Integer | Yes      | ID of the Class.                                        |
| `section`            | Integer | Yes      | ID of the Section.                                      |
| `subject_assignment` | Integer | Yes      | ID of the Subject Assignment (links subject & teacher). |
| `day_of_week`        | Integer | Yes      | 0 (Monday) to 6 (Sunday).                               |
| `class_time`         | Integer | Yes      | ID of the Class Time slot.                              |
| `classroom`          | Integer | No       | ID of the Classroom.                                    |
| `effective_from`     | Date    | Yes      | Start date (YYYY-MM-DD).                                |
| `effective_to`       | Date    | No       | End date (YYYY-MM-DD).                                  |
| `is_active`          | Boolean | No       | Default: `true`.                                        |

**Response (201 Created)**:

```json
{
  "id": 1,
  "class_obj": 101,
  "class_name": "CS-A Sem 1",
  "section": 201,
  "section_name": "Section A",
  "subject_assignment": 305,
  "subject_details": {
    "id": 501,
    "code": "CS101",
    "name": "Data Structures",
    "short_name": "DS",
    "college": 1,
    "college_name": "Engineering College",
    "subject_type": "theory",
    "credits": "4.00",
    "is_active": true
  },
  "teacher_details": {
    "id": 10,
    "username": "jdoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com"
  },
  "day_of_week": 0,
  "class_time": 15,
  "time_details": {
    "id": 15,
    "college": 1,
    "college_name": "Engineering College",
    "period_number": 1,
    "start_time": "09:00:00",
    "end_time": "10:00:00",
    "is_break": false,
    "break_name": null,
    "is_active": true,
    "created_by": 1,
    "updated_by": null,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  },
  "classroom": 50,
  "classroom_details": {
    "id": 50,
    "code": "R101",
    "name": "Room 101",
    "college": 1,
    "college_name": "Engineering College",
    "room_type": "classroom",
    "capacity": 60,
    "is_active": true
  },
  "effective_from": "2024-01-01",
  "effective_to": null,
  "is_active": true,
  "created_by": 1,
  "updated_by": null,
  "created_at": "2024-01-08T12:00:00Z",
  "updated_at": "2024-01-08T12:00:00Z"
}
```

---

### 3. Retrieve Timetable Entry

Get details of a specific timetable entry.

**Endpoint**: `GET /api/v1/academic/timetable/{id}/`

**Response (200 OK)**:
Same structure as the **Create** response.

---

### 4. Update Timetable Entry

Update an existing timetable entry.

**Endpoint**: `PUT /api/v1/academic/timetable/{id}/`

**Request Payload**:

```json
{
  "class_obj": 101,
  "section": 201,
  "subject_assignment": 305,
  "day_of_week": 1,
  "class_time": 16,
  "classroom": 51,
  "effective_from": "2024-01-01",
  "is_active": true
}
```

_(Check "Create" payload for field descriptions)_

**Response (200 OK)**:
Same structure as the **Create** response with updated values.

---

### 5. Partial Update Timetable Entry

Update specific fields of a timetable entry.

**Endpoint**: `PATCH /api/v1/academic/timetable/{id}/`

**Request Payload**:

```json
{
  "classroom": 52
}
```

**Response (200 OK)**:
Same structure as the **Create** response with updated values.

---

### 6. Delete Timetable Entry

Remove a timetable entry.

**Endpoint**: `DELETE /api/v1/academic/timetable/{id}/`

**Response (204 No Content)**:
Empty body.
