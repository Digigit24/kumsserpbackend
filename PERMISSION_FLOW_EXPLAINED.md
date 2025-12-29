# KUMSS Permission System - Complete Flow Explained

This document explains exactly which models have which permissions, how permissions flow to the frontend, and how users will behave based on their permissions.

---

## 📋 Part 1: Resource to Model Mapping

Each **resource** in the permission system maps to Django **models** and **ViewSets**. Here's the complete mapping:

| Resource | Django Models | Django App | ViewSets/APIs |
|----------|---------------|------------|---------------|
| **attendance** | `Attendance`, `AttendanceRecord` | `apps.attendance` | `AttendanceViewSet` |
| **students** | `Student`, `StudentProfile`, `StudentAdmission` | `apps.students` | `StudentViewSet`, `StudentProfileViewSet` |
| **fees** | `FeeStructure`, `FeePayment`, `FeeInvoice` | `apps.fees` | `FeeStructureViewSet`, `FeePaymentViewSet` |
| **examinations** | `Exam`, `ExamSchedule`, `ExamResult`, `Grade` | `apps.examinations` | `ExamViewSet`, `ExamResultViewSet` |
| **library** | `Book`, `BookIssue`, `BookReturn`, `LibraryMember` | `apps.library` | `BookViewSet`, `BookIssueViewSet` |
| **hr** | `Employee`, `Department`, `Designation`, `Salary` | `apps.hr` | `EmployeeViewSet`, `DepartmentViewSet` |
| **hostel** | `Hostel`, `HostelRoom`, `RoomAllocation` | `apps.hostel` | `HostelViewSet`, `RoomAllocationViewSet` |
| **academic** | `Program`, `Course`, `Subject`, `Semester` | `apps.academic` | `ProgramViewSet`, `CourseViewSet` |
| **accounting** | `Account`, `Transaction`, `Ledger`, `Budget` | `apps.accounting` | `AccountViewSet`, `TransactionViewSet` |
| **communication** | `Message`, `Notification`, `SMS`, `Email` | `apps.communication` | `MessageViewSet`, `NotificationViewSet` |
| **teachers** | `Teacher`, `TeacherProfile`, `TeacherAssignment` | `apps.teachers` | `TeacherViewSet`, `TeacherProfileViewSet` |
| **online_exam** | `OnlineExam`, `Question`, `Answer`, `ExamAttempt` | `apps.online_exam` | `OnlineExamViewSet`, `QuestionViewSet` |
| **reports** | `Report`, `ReportTemplate`, `ReportGeneration` | `apps.reports` | `ReportViewSet` |
| **store** | `StoreItem`, `StoreIssue`, `StoreReturn`, `Inventory` | `apps.store` | `StoreItemViewSet`, `StoreIssueViewSet` |
| **colleges** | `College` | `apps.core` | `CollegeViewSet` |
| **academic_years** | `AcademicYear`, `AcademicSession` | `apps.core` | `AcademicYearViewSet` |
| **holidays** | `Holiday` | `apps.core` | `HolidayViewSet` |
| **system_settings** | `SystemSetting`, `NotificationSetting` | `apps.core` | `SystemSettingViewSet` |

---

## 🔄 Part 2: Permission Flow - Backend to Frontend

Here's the **complete flow** of how permissions work from login to UI rendering:

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER LOGS IN                                                │
├─────────────────────────────────────────────────────────────────────┤
│ Frontend sends:                                                     │
│   POST /api/accounts/login/                                         │
│   Headers: X-College-ID: 1                                          │
│   Body: { username: "john_student", password: "pass123" }           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: BACKEND PROCESSES LOGIN                                     │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Authenticate user (username + password)                          │
│ 2. Get user's college: user.college_id = 1                          │
│ 3. Get user's role: user.user_type = "student"                      │
│ 4. Query Permission model:                                          │
│    Permission.objects.get(college_id=1, role="student")             │
│ 5. Get permissions_json field from database                         │
│ 6. Build login response with permissions                            │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: BACKEND RETURNS TOKEN + PERMISSIONS                         │
├─────────────────────────────────────────────────────────────────────┤
│ Response:                                                           │
│ {                                                                   │
│   "access": "JWT_TOKEN_HERE",                                       │
│   "refresh": "REFRESH_TOKEN_HERE",                                  │
│   "user": {                                                         │
│     "id": "uuid",                                                   │
│     "username": "john_student",                                     │
│     "user_type": "student",                                         │
│     "college_id": 1,                                                │
│     "user_roles": [                                                 │
│       {                                                             │
│         "role_code": "student",                                     │
│         "role_name": "Student",                                     │
│         "is_primary": true                                          │
│       }                                                             │
│     ],                                                              │
│     "user_permissions": {                  ◄─── THIS IS THE KEY!   │
│       "attendance": {                                               │
│         "read": {"enabled": true, "scope": "mine"},                 │
│         "create": {"enabled": false, "scope": "none"},              │
│         "update": {"enabled": false, "scope": "none"},              │
│         "delete": {"enabled": false, "scope": "none"}               │
│       },                                                            │
│       "students": {                                                 │
│         "read": {"enabled": true, "scope": "mine"},                 │
│         "update": {"enabled": false, "scope": "none"}               │
│       },                                                            │
│       "fees": {                                                     │
│         "read": {"enabled": true, "scope": "mine"}                  │
│       }                                                             │
│     }                                                               │
│   }                                                                 │
│ }                                                                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: FRONTEND STORES PERMISSIONS                                 │
├─────────────────────────────────────────────────────────────────────┤
│ Frontend stores in state management:                                │
│   - localStorage.setItem('user_permissions', ...)                   │
│   - Redux store: dispatch(setPermissions(...))                      │
│   - Context API: setUserPermissions(...)                            │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: FRONTEND RENDERS UI BASED ON PERMISSIONS                    │
├─────────────────────────────────────────────────────────────────────┤
│ Component checks permissions before rendering:                      │
│                                                                     │
│ // Attendance Page                                                  │
│ if (hasPermission('attendance', 'read')) {                          │
│   // Show attendance list                                           │
│   <AttendanceList />                                                │
│ }                                                                   │
│                                                                     │
│ if (hasPermission('attendance', 'create')) {                        │
│   // Show "Mark Attendance" button                                  │
│   <Button>Mark Attendance</Button>  ◄── HIDDEN for students!       │
│ }                                                                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 6: USER MAKES API REQUEST                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Frontend:                                                           │
│   GET /api/attendance/                                              │
│   Headers:                                                          │
│     Authorization: Bearer JWT_TOKEN                                 │
│     X-College-ID: 1                                                 │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 7: BACKEND VALIDATES PERMISSIONS                               │
├─────────────────────────────────────────────────────────────────────┤
│ ViewSet (AttendanceViewSet):                                        │
│   1. permission_classes = [ResourcePermission]                      │
│   2. resource_name = 'attendance'                                   │
│   3. Backend checks: user has 'read' permission on 'attendance'?    │
│   4. If YES → Continue                                              │
│   5. If NO → Return 403 Forbidden                                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 8: BACKEND APPLIES SCOPE FILTERING                             │
├─────────────────────────────────────────────────────────────────────┤
│ ScopedQuerysetMixin applies scope filter:                           │
│                                                                     │
│ User's permission scope = "mine"                                    │
│                                                                     │
│ Backend filters queryset:                                           │
│   Attendance.objects.filter(student_id=user.id)                     │
│                                           ▲                         │
│                                           │                         │
│                                     Only user's data!               │
│                                                                     │
│ Returns ONLY the student's own attendance records                   │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 9: FRONTEND RECEIVES SCOPED DATA                               │
├─────────────────────────────────────────────────────────────────────┤
│ Student sees:                                                       │
│   - Only their own attendance (scope: mine)                         │
│   - No "Create" button (enabled: false)                             │
│   - No "Edit" button (enabled: false)                               │
│   - No "Delete" button (enabled: false)                             │
│   - Only "View" and "Export My Attendance" options                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 👥 Part 3: How Different Users Behave

Let me show you **exact examples** of how different users will behave in the frontend:

### Example 1: Student User

**Login Response:**
```json
{
  "user": {
    "username": "john_student",
    "user_type": "student",
    "user_permissions": {
      "attendance": {
        "read": {"enabled": true, "scope": "mine"},
        "create": {"enabled": false, "scope": "none"},
        "update": {"enabled": false, "scope": "none"},
        "delete": {"enabled": false, "scope": "none"}
      },
      "students": {
        "read": {"enabled": true, "scope": "mine"}
      },
      "fees": {
        "read": {"enabled": true, "scope": "mine"}
      }
    }
  }
}
```

**Frontend Behavior:**

| Page | What Student Sees | What Student CANNOT See |
|------|------------------|-------------------------|
| **Attendance** | ✅ View own attendance<br>✅ Export own attendance | ❌ Mark attendance button<br>❌ Edit attendance<br>❌ Delete attendance<br>❌ Other students' attendance |
| **Students** | ✅ View own profile<br>✅ Edit own profile | ❌ View other students<br>❌ Create student<br>❌ Delete student |
| **Fees** | ✅ View own fees<br>✅ Download receipt | ❌ Create fee<br>❌ Edit fee<br>❌ Delete fee<br>❌ Generate invoice<br>❌ Other students' fees |
| **Library** | ✅ View own issued books | ❌ Issue book button<br>❌ Return book button<br>❌ Add book to library |
| **Examinations** | ✅ View own exam results | ❌ Create exam<br>❌ Edit marks<br>❌ Publish results |

---

### Example 2: Teacher User

**Login Response:**
```json
{
  "user": {
    "username": "jane_teacher",
    "user_type": "teacher",
    "user_permissions": {
      "attendance": {
        "create": {"enabled": true, "scope": "team"},
        "read": {"enabled": true, "scope": "team"},
        "update": {"enabled": true, "scope": "team"},
        "delete": {"enabled": false, "scope": "none"}
      },
      "students": {
        "read": {"enabled": true, "scope": "team"}
      },
      "examinations": {
        "create": {"enabled": true, "scope": "team"},
        "read": {"enabled": true, "scope": "team"},
        "update": {"enabled": true, "scope": "team"},
        "publish_results": {"enabled": true, "scope": "team"}
      }
    }
  }
}
```

**Frontend Behavior:**

| Page | What Teacher Sees | What Teacher CANNOT See |
|------|------------------|-------------------------|
| **Attendance** | ✅ Mark attendance for their students<br>✅ View attendance for their students<br>✅ Edit attendance for their students<br>✅ Export attendance reports | ❌ Delete attendance<br>❌ See other teachers' students |
| **Students** | ✅ View their assigned students<br>✅ Export student list | ❌ Create new student<br>❌ Edit student info<br>❌ Delete student<br>❌ See unassigned students |
| **Examinations** | ✅ Create exams for their subject<br>✅ Enter marks for their students<br>✅ Publish results<br>✅ View exam reports | ❌ Edit other teachers' exams<br>❌ Delete exams |
| **Fees** | ❌ No access to fee module | ❌ Everything hidden |

**Important: "team" scope means:**
- Backend fetches students assigned to this teacher via `TeamMembership` model
- Teacher only sees students they teach
- Uses relationship: `leader=teacher, member=student, resource='students'`

---

### Example 3: Admin User

**Login Response:**
```json
{
  "user": {
    "username": "admin_user",
    "user_type": "admin",
    "user_permissions": {
      "attendance": {
        "create": {"enabled": true, "scope": "all"},
        "read": {"enabled": true, "scope": "all"},
        "update": {"enabled": true, "scope": "all"},
        "delete": {"enabled": true, "scope": "all"}
      },
      "students": {
        "create": {"enabled": true, "scope": "all"},
        "read": {"enabled": true, "scope": "all"},
        "update": {"enabled": true, "scope": "all"},
        "delete": {"enabled": true, "scope": "all"}
      },
      "fees": {
        "create": {"enabled": true, "scope": "all"},
        "read": {"enabled": true, "scope": "all"},
        "update": {"enabled": true, "scope": "all"},
        "delete": {"enabled": true, "scope": "all"}
      }
      // ... ALL resources have ALL actions enabled with "all" scope
    }
  }
}
```

**Frontend Behavior:**

| Page | What Admin Sees |
|------|----------------|
| **All Pages** | ✅ Everything!<br>✅ All buttons visible<br>✅ All data visible<br>✅ Can create, read, update, delete everything<br>✅ Sees all students, teachers, staff |
| **Navigation** | ✅ All menu items visible<br>✅ All modules accessible |

---

### Example 4: HOD (Head of Department) User

**Login Response:**
```json
{
  "user": {
    "username": "hod_user",
    "user_type": "hod",
    "department_id": 5,
    "user_permissions": {
      "attendance": {
        "create": {"enabled": true, "scope": "department"},
        "read": {"enabled": true, "scope": "department"},
        "update": {"enabled": true, "scope": "department"},
        "delete": {"enabled": true, "scope": "department"}
      },
      "students": {
        "create": {"enabled": true, "scope": "department"},
        "read": {"enabled": true, "scope": "department"},
        "update": {"enabled": true, "scope": "department"},
        "delete": {"enabled": true, "scope": "department"}
      }
      // ... ALL resources have ALL actions with "department" scope
    }
  }
}
```

**Frontend Behavior:**

| Page | What HOD Sees | What HOD CANNOT See |
|------|--------------|---------------------|
| **Students** | ✅ All students in their department<br>✅ Create, edit, delete students in dept | ❌ Students from other departments |
| **Teachers** | ✅ All teachers in their department<br>✅ Assign subjects to dept teachers | ❌ Teachers from other departments |
| **Attendance** | ✅ All attendance for dept students<br>✅ Generate dept reports | ❌ Attendance from other departments |

---

## 🎯 Part 4: Real-World UI Examples

### Example: Attendance Page for Different Users

**Student View:**
```html
<div class="attendance-page">
  <h1>My Attendance</h1>

  <!-- Only visible to student -->
  <table>
    <tr>
      <td>Date</td>
      <td>Status</td>
    </tr>
    <tr>
      <td>2024-01-15</td>
      <td>Present</td>
    </tr>
    <!-- Only shows student's own records -->
  </table>

  <!-- NO buttons for create/edit/delete -->
  <!-- Only has "Export My Attendance" button -->
  <button>Export My Attendance</button>
</div>
```

**Teacher View:**
```html
<div class="attendance-page">
  <h1>Attendance Management</h1>

  <!-- Teacher sees additional controls -->
  <button>Mark Attendance</button>  ← NEW!
  <button>Bulk Update</button>      ← NEW!

  <table>
    <tr>
      <td>Student Name</td>
      <td>Date</td>
      <td>Status</td>
      <td>Actions</td>
    </tr>
    <tr>
      <td>John Student</td>
      <td>2024-01-15</td>
      <td>Present</td>
      <td>
        <button>Edit</button>    ← NEW!
        <!-- NO Delete button - teacher can't delete -->
      </td>
    </tr>
    <!-- Shows all students assigned to this teacher -->
  </table>

  <button>Export Report</button>
</div>
```

**Admin View:**
```html
<div class="attendance-page">
  <h1>Attendance Management (All College)</h1>

  <!-- Admin sees ALL controls -->
  <button>Mark Attendance</button>
  <button>Bulk Update</button>
  <button>Import Attendance</button>  ← NEW!

  <!-- Filters for all departments, classes -->
  <select name="department">...</select>
  <select name="class">...</select>

  <table>
    <tr>
      <td>Student Name</td>
      <td>Class</td>
      <td>Date</td>
      <td>Status</td>
      <td>Actions</td>
    </tr>
    <tr>
      <td>John Student</td>
      <td>Class 10A</td>
      <td>2024-01-15</td>
      <td>Present</td>
      <td>
        <button>Edit</button>
        <button>Delete</button>  ← NEW! (Admin can delete)
      </td>
    </tr>
    <!-- Shows ALL students across entire college -->
  </table>
</div>
```

---

## 🔒 Part 5: Backend Enforcement (Double Protection)

**Important:** Frontend hiding buttons is NOT enough for security. Backend ALWAYS validates permissions:

### Backend ViewSet Example

```python
# apps/attendance/views.py
from apps.core.permissions.drf_permissions import ResourcePermission
from apps.core.mixins import CollegeScopedModelViewSet

class AttendanceViewSet(CollegeScopedModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = 'attendance'  ← This ties to permission system

    # Backend automatically:
    # 1. Checks if user has permission for the action
    # 2. Applies scope filtering (mine/team/department/all)
    # 3. Returns 403 if no permission
```

### What Happens When Student Tries to Create Attendance

**Frontend:** Button is hidden (student never sees "Mark Attendance" button)

**BUT if student bypasses frontend (Postman, curl, browser console):**

```http
POST /api/attendance/
Authorization: Bearer student_token
X-College-ID: 1

{
  "student_id": 123,
  "date": "2024-01-15",
  "status": "present"
}
```

**Backend Response:**
```http
HTTP 403 Forbidden

{
  "detail": "You do not have permission to perform this action.",
  "required_permission": "attendance.create",
  "user_role": "student",
  "permission_enabled": false
}
```

---

## ✅ Part 6: Summary - Will It Work?

### YES! Here's why:

| Question | Answer |
|----------|--------|
| **Will permissions reflect in frontend?** | ✅ YES - Login response includes complete `user_permissions` object |
| **Will students see limited UI?** | ✅ YES - Frontend checks permissions before rendering buttons/pages |
| **Will teachers see only their students?** | ✅ YES - Backend applies "team" scope filtering via TeamMembership |
| **Will admins see everything?** | ✅ YES - "all" scope returns all records |
| **Can users bypass frontend restrictions?** | ❌ NO - Backend validates every API request |
| **Do permissions persist across sessions?** | ✅ YES - Stored in localStorage/Redux, refreshed on login |
| **Can admin customize permissions?** | ✅ YES - Edit Permission records in database or via admin API |

---

## 🚀 Part 7: How Frontend Developer Uses Permissions

### Step 1: Get Permissions from Login Response

```javascript
// After login
const loginResponse = await api.login(username, password);
const permissions = loginResponse.user.user_permissions;

// Store in state
localStorage.setItem('permissions', JSON.stringify(permissions));
dispatch(setPermissions(permissions));
```

### Step 2: Create Helper Functions

```javascript
// utils/permissions.js
export function hasPermission(resource, action) {
  const permissions = JSON.parse(localStorage.getItem('permissions'));
  return permissions?.[resource]?.[action]?.enabled || false;
}

export function getScope(resource, action) {
  const permissions = JSON.parse(localStorage.getItem('permissions'));
  return permissions?.[resource]?.[action]?.scope || 'none';
}
```

### Step 3: Use in Components

```jsx
// pages/AttendancePage.jsx
import { hasPermission } from '@/utils/permissions';

function AttendancePage() {
  return (
    <div>
      <h1>Attendance</h1>

      {hasPermission('attendance', 'create') && (
        <button onClick={markAttendance}>Mark Attendance</button>
      )}

      {hasPermission('attendance', 'read') && (
        <AttendanceList />
      )}

      {hasPermission('attendance', 'update') && (
        <button onClick={editAttendance}>Edit</button>
      )}

      {hasPermission('attendance', 'delete') && (
        <button onClick={deleteAttendance}>Delete</button>
      )}
    </div>
  );
}
```

---

## 📊 Part 8: Permission Matrix (All Roles)

| Resource | Student | Teacher | HOD | Admin | Staff |
|----------|---------|---------|-----|-------|-------|
| **Attendance** | Read (mine) | Create, Read, Update (team) | All (dept) | All (all) | - |
| **Students** | Read (mine) | Read (team) | All (dept) | All (all) | Create, Read, Update (all) |
| **Fees** | Read (mine) | - | All (dept) | All (all) | - |
| **Examinations** | Read (mine) | Create, Read, Update, Publish (team) | All (dept) | All (all) | - |
| **Library** | Read (mine) | Read (all) | All (dept) | All (all) | All (all) |
| **Online Exam** | Read (mine) | All (team) | All (dept) | All (all) | - |
| **Reports** | - | Read, Generate (team) | All (dept) | All (all) | - |

**Legend:**
- **Read (mine)** = Can only see their own data
- **Read (team)** = Can see assigned students/subjects
- **Read (dept)** = Can see entire department
- **Read (all)** = Can see entire college
- **All** = Can Create, Read, Update, Delete
- **-** = No access at all

---

## 🎓 Final Answer to Your Questions

### Q1: Which models have which permissions?
**A:** Every Django model maps to a resource (see Part 1 table). Each resource has specific actions (create, read, update, delete, etc.) defined in `PERMISSION_REGISTRY`.

### Q2: Will it reflect to frontend users?
**A:** YES! The login response includes `user_permissions` object with every permission. Frontend stores this and uses it to show/hide UI elements (see Part 2 flow diagram).

### Q3: Will users behave according to permissions?
**A:** YES! Users will behave exactly according to permissions in TWO ways:
1. **Frontend:** Buttons/pages are hidden if permission is disabled
2. **Backend:** API requests are blocked if permission is disabled (even if user bypasses frontend)

### Example Flow:
1. Student logs in → Gets `attendance.create = false`
2. Frontend hides "Mark Attendance" button
3. If student tries API directly → Backend returns 403 Forbidden
4. Student can ONLY see their own attendance (scope: mine)
5. Teacher logs in → Gets `attendance.create = true, scope: team`
6. Frontend shows "Mark Attendance" button
7. Teacher can mark attendance for assigned students only
8. Backend filters to show only assigned students

---

**The permission system is complete, secure, and ready to use!** 🎉
