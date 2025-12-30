# KUMSS ERP - Complete API Endpoints Documentation

## Base URL: `http://127.0.0.1:8000/api/v1/`

---

## 1. ACCOUNTS APP (`/api/v1/accounts/`)

### Endpoints:
- `POST /api/v1/auth/login/` - Login (custom override)
- `GET /api/v1/accounts/users/` - List users
- `POST /api/v1/accounts/users/` - Create user
- `GET /api/v1/accounts/users/{id}/` - Get user details
- `PUT /api/v1/accounts/users/{id}/` - Update user
- `DELETE /api/v1/accounts/users/{id}/` - Delete user
- `GET /api/v1/accounts/user-profiles/` - List user profiles
- `POST /api/v1/accounts/user-profiles/` - Create user profile
- `GET /api/v1/accounts/user-profiles/{id}/` - Get user profile
- `PUT /api/v1/accounts/user-profiles/{id}/` - Update user profile
- `GET /api/v1/accounts/roles/` - List roles
- `POST /api/v1/accounts/roles/` - Create role
- `GET /api/v1/accounts/user-roles/` - List user roles
- `POST /api/v1/accounts/user-roles/` - Assign role to user
- `GET /api/v1/accounts/permissions/` - List permissions
- `GET /api/v1/accounts/team-memberships/` - List team memberships

---

## 2. CORE APP (`/api/v1/core/`)

### Endpoints:
- `GET /api/v1/core/colleges/` - List colleges
- `POST /api/v1/core/colleges/` - Create college
- `GET /api/v1/core/colleges/{id}/` - Get college details
- `PUT /api/v1/core/colleges/{id}/` - Update college
- `GET /api/v1/core/academic-years/` - List academic years
- `POST /api/v1/core/academic-years/` - Create academic year
- `GET /api/v1/core/academic-sessions/` - List academic sessions
- `POST /api/v1/core/academic-sessions/` - Create academic session
- `GET /api/v1/core/holidays/` - List holidays
- `POST /api/v1/core/holidays/` - Create holiday
- `GET /api/v1/core/weekends/` - List weekends
- `GET /api/v1/core/system-settings/` - List system settings
- `GET /api/v1/core/notification-settings/` - List notification settings
- `GET /api/v1/core/activity-logs/` - List activity logs
- `GET /api/v1/core/departments/` - List departments
- `POST /api/v1/core/departments/` - Create department

---

## 3. ACADEMIC APP (`/api/v1/academic/`)

### Endpoints:
- `GET /api/v1/academic/faculties/` - List faculties
- `POST /api/v1/academic/faculties/` - Create faculty
- `GET /api/v1/academic/faculties/{id}/` - Get faculty details
- `GET /api/v1/academic/programs/` - List programs
- `POST /api/v1/academic/programs/` - Create program
- `GET /api/v1/academic/classes/` - List classes
- `POST /api/v1/academic/classes/` - Create class
- `GET /api/v1/academic/sections/` - List sections
- `POST /api/v1/academic/sections/` - Create section
- `GET /api/v1/academic/subjects/` - List subjects
- `POST /api/v1/academic/subjects/` - Create subject
- `GET /api/v1/academic/optional-subjects/` - List optional subjects
- `GET /api/v1/academic/subject-assignments/` - List subject assignments
- `POST /api/v1/academic/subject-assignments/` - Assign subject to teacher
- `GET /api/v1/academic/classrooms/` - List classrooms
- `POST /api/v1/academic/classrooms/` - Create classroom
- `GET /api/v1/academic/class-times/` - List class times
- `GET /api/v1/academic/timetable/` - List timetable
- `POST /api/v1/academic/timetable/` - Create timetable entry
- `GET /api/v1/academic/lab-schedules/` - List lab schedules
- `GET /api/v1/academic/class-teachers/` - List class teachers

---

## 4. STUDENTS APP (`/api/v1/students/`)

### Endpoints:
- `GET /api/v1/students/students/` - List students
- `POST /api/v1/students/students/` - Create student
- `GET /api/v1/students/students/{id}/` - Get student details
- `PUT /api/v1/students/students/{id}/` - Update student
- `DELETE /api/v1/students/students/{id}/` - Delete student
- `GET /api/v1/students/categories/` - List student categories
- `GET /api/v1/students/groups/` - List student groups
- `GET /api/v1/students/guardians/` - List guardians
- `POST /api/v1/students/guardians/` - Create guardian
- `GET /api/v1/students/student-guardians/` - List student-guardian relationships
- `GET /api/v1/students/addresses/` - List student addresses
- `GET /api/v1/students/documents/` - List student documents
- `POST /api/v1/students/documents/` - Upload student document
- `GET /api/v1/students/medical-records/` - List medical records
- `GET /api/v1/students/previous-records/` - List previous academic records
- `GET /api/v1/students/id-cards/` - List student ID cards
- `GET /api/v1/students/promotions/` - List student promotions
- `POST /api/v1/students/promotions/` - Promote students

---

## 5. TEACHERS APP (`/api/v1/teachers/`)

### Endpoints:
- `GET /api/v1/teachers/teachers/` - List teachers
- `POST /api/v1/teachers/teachers/` - Create teacher
- `GET /api/v1/teachers/teachers/{id}/` - Get teacher details
- `PUT /api/v1/teachers/teachers/{id}/` - Update teacher
- `GET /api/v1/teachers/teachers/me/` - Get current teacher profile ✨ NEW
- `GET /api/v1/teachers/study-materials/` - List study materials
- `POST /api/v1/teachers/study-materials/` - Upload study material
- `GET /api/v1/teachers/assignments/` - List assignments
- `POST /api/v1/teachers/assignments/` - Create assignment ✨ FIXED
- `GET /api/v1/teachers/assignments/{id}/` - Get assignment details
- `PUT /api/v1/teachers/assignments/{id}/` - Update assignment
- `DELETE /api/v1/teachers/assignments/{id}/` - Delete assignment
- `GET /api/v1/teachers/assignment-submissions/` - List submissions
- `GET /api/v1/teachers/homework/` - List homework
- `POST /api/v1/teachers/homework/` - Create homework
- `GET /api/v1/teachers/homework-submissions/` - List homework submissions

---

## 6. ATTENDANCE APP (`/api/v1/attendance/`)

### Endpoints:
- `GET /api/v1/attendance/student-attendance/` - List student attendance
- `POST /api/v1/attendance/student-attendance/` - Mark student attendance
- `GET /api/v1/attendance/subject-attendance/` - List subject-wise attendance
- `GET /api/v1/attendance/staff-attendance/` - List staff attendance
- `POST /api/v1/attendance/staff-attendance/` - Mark staff attendance
- `GET /api/v1/attendance/notifications/` - List attendance notifications
- `GET /api/v1/attendance/notification-rules/` - List notification rules

---

## 7. FEES APP (`/api/v1/fees/`)

### Endpoints:
- `GET /api/v1/fees/fee-types/` - List fee types
- `POST /api/v1/fees/fee-types/` - Create fee type
- `GET /api/v1/fees/fee-groups/` - List fee groups
- `GET /api/v1/fees/fee-masters/` - List fee masters
- `GET /api/v1/fees/fee-structures/` - List fee structures
- `POST /api/v1/fees/fee-structures/` - Create fee structure
- `GET /api/v1/fees/fee-installments/` - List fee installments
- `GET /api/v1/fees/fee-collections/` - List fee collections
- `POST /api/v1/fees/fee-collections/` - Collect fee
- `GET /api/v1/fees/fee-receipts/` - List fee receipts
- `GET /api/v1/fees/fee-discounts/` - List fee discounts
- `GET /api/v1/fees/student-fee-discounts/` - List student-specific discounts
- `GET /api/v1/fees/fee-fines/` - List fee fines
- `GET /api/v1/fees/fee-refunds/` - List fee refunds
- `GET /api/v1/fees/fee-reminders/` - List fee reminders
- `GET /api/v1/fees/online-payments/` - List online payments
- `GET /api/v1/fees/bank-payments/` - List bank payments

---

## 8. ACCOUNTING APP (`/api/v1/accounting/`)

### Endpoints:
- `GET /api/v1/accounting/accounts/` - List accounts
- `POST /api/v1/accounting/accounts/` - Create account
- `GET /api/v1/accounting/account-transactions/` - List transactions
- `POST /api/v1/accounting/account-transactions/` - Create transaction
- `GET /api/v1/accounting/vouchers/` - List vouchers
- `GET /api/v1/accounting/financial-years/` - List financial years
- `GET /api/v1/accounting/income-categories/` - List income categories
- `GET /api/v1/accounting/expense-categories/` - List expense categories
- `GET /api/v1/accounting/income/` - List income
- `POST /api/v1/accounting/income/` - Record income
- `GET /api/v1/accounting/expenses/` - List expenses
- `POST /api/v1/accounting/expenses/` - Record expense

---

## 9. EXAMINATIONS APP (`/api/v1/examinations/`)

### Endpoints:
- `GET /api/v1/examinations/exam-types/` - List exam types
- `GET /api/v1/examinations/exams/` - List exams
- `POST /api/v1/examinations/exams/` - Create exam
- `GET /api/v1/examinations/exam-schedules/` - List exam schedules
- `POST /api/v1/examinations/exam-schedules/` - Create exam schedule
- `GET /api/v1/examinations/exam-attendance/` - List exam attendance
- `GET /api/v1/examinations/marks-registers/` - List marks registers
- `GET /api/v1/examinations/student-marks/` - List student marks
- `POST /api/v1/examinations/student-marks/` - Enter marks
- `GET /api/v1/examinations/exam-results/` - List exam results
- `GET /api/v1/examinations/marks-grades/` - List marks grades
- `GET /api/v1/examinations/mark-sheets/` - List mark sheets
- `GET /api/v1/examinations/progress-cards/` - List progress cards
- `GET /api/v1/examinations/tabulation-sheets/` - List tabulation sheets
- `GET /api/v1/examinations/admit-cards/` - List admit cards
- `GET /api/v1/examinations/certificates/` - List certificates

---

## 10. ONLINE EXAM APP (`/api/v1/online-exam/`)

### Endpoints:
- `GET /api/v1/online-exam/online-exams/` - List online exams
- `POST /api/v1/online-exam/online-exams/` - Create online exam
- `GET /api/v1/online-exam/questions/` - List questions
- `POST /api/v1/online-exam/questions/` - Create question
- `GET /api/v1/online-exam/question-options/` - List question options
- `GET /api/v1/online-exam/question-banks/` - List question banks
- `GET /api/v1/online-exam/exam-questions/` - List exam questions
- `GET /api/v1/online-exam/student-exam-attempts/` - List student attempts
- `POST /api/v1/online-exam/student-exam-attempts/` - Start exam attempt
- `GET /api/v1/online-exam/student-answers/` - List student answers
- `POST /api/v1/online-exam/student-answers/` - Submit answer

---

## 11. HOSTEL APP (`/api/v1/hostel/`)

### Endpoints:
- `GET /api/v1/hostel/hostels/` - List hostels
- `POST /api/v1/hostel/hostels/` - Create hostel
- `GET /api/v1/hostel/room-types/` - List room types
- `GET /api/v1/hostel/rooms/` - List rooms
- `POST /api/v1/hostel/rooms/` - Create room
- `GET /api/v1/hostel/beds/` - List beds
- `GET /api/v1/hostel/allocations/` - List hostel allocations
- `POST /api/v1/hostel/allocations/` - Allocate hostel
- `GET /api/v1/hostel/fees/` - List hostel fees

---

## 12. LIBRARY APP (`/api/v1/library/`)

### Endpoints:
- `GET /api/v1/library/books/` - List books
- `POST /api/v1/library/books/` - Add book
- `GET /api/v1/library/books/{id}/` - Get book details
- `PUT /api/v1/library/books/{id}/` - Update book
- `GET /api/v1/library/categories/` - List book categories
- `GET /api/v1/library/members/` - List library members
- `GET /api/v1/library/cards/` - List library cards
- `GET /api/v1/library/issues/` - List book issues
- `POST /api/v1/library/issues/` - Issue book
- `GET /api/v1/library/returns/` - List book returns
- `POST /api/v1/library/returns/` - Return book
- `GET /api/v1/library/reservations/` - List book reservations
- `GET /api/v1/library/fines/` - List library fines

---

## 13. STORE APP (`/api/v1/store/`)

### Endpoints:
- `GET /api/v1/store/categories/` - List store categories
- `GET /api/v1/store/items/` - List store items
- `POST /api/v1/store/items/` - Create store item
- `GET /api/v1/store/vendors/` - List vendors
- `POST /api/v1/store/vendors/` - Create vendor
- `GET /api/v1/store/stock-receipts/` - List stock receipts
- `POST /api/v1/store/stock-receipts/` - Receive stock
- `GET /api/v1/store/sales/` - List sales
- `POST /api/v1/store/sales/` - Record sale
- `GET /api/v1/store/sale-items/` - List sale items
- `GET /api/v1/store/credits/` - List store credits

---

## 14. HR APP (`/api/v1/hr/`)

### Endpoints:
- `GET /api/v1/hr/salary-components/` - List salary components
- `GET /api/v1/hr/salary-structures/` - List salary structures
- `POST /api/v1/hr/salary-structures/` - Create salary structure
- `GET /api/v1/hr/payroll-items/` - List payroll items
- `GET /api/v1/hr/payrolls/` - List payrolls
- `POST /api/v1/hr/payrolls/` - Generate payroll
- `GET /api/v1/hr/payslips/` - List payslips
- `GET /api/v1/hr/deductions/` - List deductions
- `GET /api/v1/hr/leave-types/` - List leave types
- `GET /api/v1/hr/leave-applications/` - List leave applications
- `POST /api/v1/hr/leave-applications/` - Apply for leave
- `GET /api/v1/hr/leave-approvals/` - List leave approvals
- `GET /api/v1/hr/leave-balances/` - List leave balances

---

## 15. COMMUNICATION APP (`/api/v1/communication/`)

### Endpoints:
- `GET /api/v1/communication/notices/` - List notices
- `POST /api/v1/communication/notices/` - Create notice
- `GET /api/v1/communication/notice-visibility/` - List notice visibility
- `GET /api/v1/communication/events/` - List events
- `POST /api/v1/communication/events/` - Create event
- `GET /api/v1/communication/event-registrations/` - List event registrations
- `GET /api/v1/communication/chats/` - List chat messages
- `POST /api/v1/communication/chats/` - Send message
- `GET /api/v1/communication/bulk-messages/` - List bulk messages
- `POST /api/v1/communication/bulk-messages/` - Send bulk message
- `GET /api/v1/communication/message-templates/` - List message templates
- `GET /api/v1/communication/message-logs/` - List message logs

---

## 16. REPORTS APP (`/api/v1/reports/`)

### Endpoints:
- `GET /api/v1/reports/templates/` - List report templates
- `POST /api/v1/reports/templates/` - Create report template
- `GET /api/v1/reports/saved/` - List saved reports
- `GET /api/v1/reports/generated/` - List generated reports
- `POST /api/v1/reports/generated/` - Generate report
- `GET /api/v1/reports/print-jobs/` - List print jobs

---

## 17. STATS APP (`/api/v1/stats/`)

### Statistics Endpoints:
- `GET /api/v1/stats/dashboard/` - Dashboard statistics
- `GET /api/v1/stats/academic/` - Academic statistics
- `GET /api/v1/stats/financial/` - Financial statistics
- `GET /api/v1/stats/library/` - Library statistics
- `GET /api/v1/stats/hostel/` - Hostel statistics
- `GET /api/v1/stats/store/` - Store statistics
- `GET /api/v1/stats/hr/` - HR statistics
- `GET /api/v1/stats/communication/` - Communication statistics
- `GET /api/v1/stats/my/` - Student's personal statistics
- `GET /api/v1/stats/my-teacher/` - Teacher's personal statistics

---

## 18. AUTHENTICATION ENDPOINTS

### dj-rest-auth (Django REST Auth):
- `POST /api/v1/auth/login/` - Login (overridden by custom view)
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/password/change/` - Change password
- `POST /api/v1/auth/password/reset/` - Reset password (request)
- `POST /api/v1/auth/password/reset/confirm/` - Reset password (confirm)
- `GET /api/v1/auth/user/` - Get current user details

---

## 19. API DOCUMENTATION

- `GET /api/schema/` - OpenAPI schema (JSON)
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation

---

## SUMMARY

**Total Apps:** 17
**Estimated Total Endpoints:** 300+

### Breakdown by App:
- **Accounts:** ~15 endpoints
- **Core:** ~14 endpoints
- **Academic:** ~23 endpoints
- **Students:** ~18 endpoints
- **Teachers:** ~15 endpoints (including new /me endpoint)
- **Attendance:** ~7 endpoints
- **Fees:** ~18 endpoints
- **Accounting:** ~12 endpoints
- **Examinations:** ~16 endpoints
- **Online Exam:** ~11 endpoints
- **Hostel:** ~9 endpoints
- **Library:** ~13 endpoints
- **Store:** ~11 endpoints
- **HR:** ~13 endpoints
- **Communication:** ~11 endpoints
- **Reports:** ~6 endpoints
- **Stats:** ~10 endpoints
- **Auth:** ~6 endpoints

---

## NOTES

✨ **NEW ENDPOINTS ADDED:**
- `/api/v1/teachers/teachers/me/` - Get current teacher profile

🔧 **FIXED ENDPOINTS:**
- `/api/v1/teachers/assignments/` - Now auto-creates teacher profile and properly scopes by college

📝 **All endpoints support:**
- College scoping via `X-College-ID` header
- Authentication via `Authorization: Token <token>`
- Standard REST operations (GET, POST, PUT, PATCH, DELETE)
- Filtering, searching, ordering, and pagination
