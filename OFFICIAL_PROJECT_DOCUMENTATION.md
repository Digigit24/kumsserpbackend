# KUMSS ERP - Comprehensive Technical Documentation

**Date:** 2025-12-30
**Version:** 1.1.0
**Confidentiality:** Internal / Senior Technical Review

---

## 1. Executive Summary

The **KUMSS ERP (Knowledge & University Management System)** is a high-performance, multi-tenant enterprise solution engineered to digitize the entire operational lifecycle of educational institutions. Built on a robust Python/Django stack, it serves as a centralized platform for academic delivery, financial governance, communication, and administrative oversight. The system distinguishes itself through a strict **Row-Level Multi-Tenancy** architecture, allowing a single deployment to serve multiple colleges securely, with data isolation enforced at the database query layer.

---

## 2. System Statistics & Metrics

A static analysis of the codebase (v1.1.0) yields the following precise metrics:

| Metric                        | Count     | Notes                                                   |
| :---------------------------- | :-------- | :------------------------------------------------------ |
| **Functional Modules (Apps)** | **17**    | Distinct business domains (e.g., Fees, Exams, HR)       |
| **Total Database Models**     | **137**   | Normalized relational entities (PostgreSQL)             |
| **Total URL Endpoints**       | **1,165** | Total addressable resources (including Admin & Debug)   |
| **Business API Endpoints**    | **~300**  | Pure REST API endpoints for frontend/mobile consumption |
| **API Resources**             | **161**   | High-level ViewSets/Controllers                         |
| **Authentication Providers**  | **2**     | `dj-rest-auth` (Token) & `django-allauth` (Session)     |

---

## 3. Detailed Architecture

### 3.1. Unified Multi-Tenancy (The "College" Scope)

Unlike simple SaaS apps that use separate schemas, KUMSS uses a **Shared-Database, Shared-Schema** approach for maximum efficiency.

- **Identification**: Every request identifies the tenant via the `X-College-ID` HTTP Header.
- **Enforcement**:
  - **Model Layer**: 90% of models inherit from `CollegeScopedModel`. This Abstract Base Class (ABC) adds a `college_id` foreign key.
  - **Manager Layer**: The custom `CollegeManager` intercepts all ORM calls (`objects.all()`, `objects.filter()`). It automatically injects `WHERE college_id = <current_id>`, preventing developers from accidentally leaking data across tenants.
  - **Middleware**: Custom middleware extracts the header and sets thread-local storage for the Manager to access.

### 3.2. Automated Consistency (Signals)

We utilize Django Signals (`post_save`, `pre_save`) to enforce business invariants:

- **Auto-Configuration**: Creating a `College` automatically spawns its `NotificationSetting` and default `Weekend` configurations.
- **Mutex Logic**: In `AcademicYear`, setting one year to `is_current=True` triggers an atomic transaction that sets all others to `False`.

### 3.3. Security & Audit

- **RBAC**: A dynamic `Permission` model stores access rules as JSON per role per college, allowing runtime permission changes without code deploys.
- **Audit Logging**: The `ActivityLog` model captures `IP Address`, `User Agent`, `User`, `Action`, and `Payload` for every critical mutation.

---

## 4. Application Modules (Detailed Breakdown)

The system is divided into 17 isolated applications. Below is the breakdown of each module, its data models, and endpoint footprint.

### 1. Core Module (`apps.core`)

- **Models**: 13
- **Endpoints**: 25
- **Description**: The kernel of the system. It manages the multi-tenancy configuration, global settings, and academic calendar foundation.
- **Key Models**:
  - `College`: The tenant entity.
  - `AcademicYear` & `AcademicSession`: Defines time-bound academic periods (e.g., 2025-26, Sem 1).
  - `SystemSetting` & `NotificationSetting`: Global configuration toggles.
  - `ActivityLog`: The central audit trail table.
  - `Permission`: Dynamic RBAC configurations.

### 2. Accounts Module (`apps.accounts`)

- **Models**: 5
- **Endpoints**: 18
- **Description**: Handles identity, authentication, and user profiles. Uses a custom UUID-based User model.
- **Key Models**:
  - `User`: Custom user model (UUID primary key).
  - `Role` & `UserRole`: Defines what a user is (e.g., "Dean", "Student") within a specific college.
  - `UserProfile`: Stores extended bio-data (address, blood group, etc.).
  - `Department`: Academic departments (CS, ME, etc.).

### 3. Students Module (`apps.students`)

- **Models**: 12
- **Endpoints**: 24
- **Description**: Manages the complete lifecycle of a student from admission to alumni status.
- **Key Models**:
  - `Student`: The core student record.
  - `Guardian` & `StudentGuardian`: Parent/Guardian relationships.
  - `StudentCategory` & `StudentGroup`: Classification (e.g., "General", "Section A").
  - `StudentDocument`: Digital locker for certificates/files.
  - `StudentPromotion`: History of movement between classes.

### 4. Fees Module (`apps.fees`)

- **Models**: 14
- **Endpoints**: 28
- **Description**: A complex financial engine capable of handling varied fee structures, discounts, fines, and receipts.
- **Key Models**:
  - `FeeStructure`: Defines how much to charge (Tuition + Lab + Library).
  - `FeeCollection` & `FeeInstallment`: Tracks what is due vs. paid.
  - `FeeReceipt`: Official payment records.
  - `FeeFine` & `FeeDiscount`: Adjustments to the base fee.
  - `OnlinePayment` & `BankPayment`: Transaction logs.

### 5. Examinations Module (`apps.examinations`)

- **Models**: 12
- **Endpoints**: 24
- **Description**: Manages traditional physical examinations, grading, and report card generation.
- **Key Models**:
  - `Exam`: An exam event (e.g., "Mid-Term 2025").
  - `ExamSchedule`: Time table for exams.
  - `AdmitCard`: Hall tickets generation.
  - `StudentMarks` & `ExamResult`: The actual scoring data.
  - `TabulationSheet`: Consolidated wide-format result sheets.

### 6. Academic Module (`apps.academic`)

- **Models**: 12
- **Endpoints**: 24
- **Description**: Defines the structural hierarchy of education delivery.
- **Key Models**:
  - `Program` (Degree), `Class` (Year), `Section` (Division).
  - `Subject` & `OptionalSubject`: Course catalog.
  - `Timetable` & `ClassTime`: Weekly scheduling.
  - `Classroom`: Physical room resource management.

### 7. HR / Payroll Module (`apps.hr`)

- **Models**: 10
- **Endpoints**: 20
- **Description**: Human Resource Management System (HRMS) for staff.
- **Key Models**:
  - `LeaveApplication` & `LeaveBalance`: Time-off management.
  - `Payroll` & `Payslip`: Monthly salary generation.
  - `SalaryStructure`: Base salary + Allowances - Deductions logic.

### 8. Communication Module (`apps.communication`)

- **Models**: 9
- **Endpoints**: 18
- **Description**: Notification engine sending SMS, Email, and WhatsApp messages.
- **Key Models**:
  - `Notice`: Digital bulletin board posts.
  - `Event`: Calendar events involved in RSVP.
  - `BulkMessage` & `MessageLog`: History of sent communications.
  - `ChatMessage`: Internal real-time messaging data.

### 9. Accounting Module (`apps.accounting`)

- **Models**: 8
- **Endpoints**: 16
- **Description**: Double-entry bookkeeping system for college expenses and income visualization.
- **Key Models**:
  - `Income` & `Expense`: General ledger entries.
  - `Voucher`: Proof of transaction.
  - `FinancialYear`: Alignment with tax years.

### 10. Library Module (`apps.library`)

- **Models**: 8
- **Endpoints**: 16
- **Description**: Library Management System (LMS) for book circulation.
- **Key Models**:
  - `Book`: Inventory of physical books.
  - `BookIssue` & `BookReturn`: Circulation logs.
  - `LibraryMember`: Who is allowed to borrow.
  - `LibraryFine`: Overdue penalties.

### 11. Store / Inventory Module (`apps.store`)

- **Models**: 8
- **Endpoints**: 16
- **Description**: Inventory management for assets (computers, desks, chalk, etc.).
- **Key Models**:
  - `StoreItem` & `Vendor`: Product and supplier master data.
  - `StockReceive` & `StoreSale`: Inward and outward movement.

### 12. Online Exam Module (`apps.online_exam`)

- **Models**: 7
- **Endpoints**: 14
- **Description**: Computer Based Testing (CBT) platform.
- **Key Models**:
  - `QuestionBank` & `Question`: Repository of MCQs/Subjective questions.
  - `OnlineExam`: The test instance.
  - `StudentExamAttempt`: The student's session.

### 13. Teachers Module (`apps.teachers`)

- **Models**: 6
- **Endpoints**: 13
- **Description**: Tools specifically for faculty usage.
- **Key Models**:
  - `Teacher`: Profile extension for staff.
  - `Assignment` & `Homework`: Tasks given to students.
  - `StudyMaterial`: File sharing (PDFs/Notes).

### 14. Hostel Module (`apps.hostel`)

- **Models**: 6
- **Endpoints**: 12
- **Description**: Residential management.
- **Key Models**:
  - `Hostel` & `Room`: Infrastructure map.
  - `HostelAllocation`: Mapping students to beds.

### 15. Attendance Module (`apps.attendance`)

- **Models**: 4
- **Endpoints**: 9
- **Description**: Time-tracking for students and staff.
- **Key Models**:
  - `StudentAttendance`: Daily/Subject-wise registers.
  - `StaffAttendance`: Biometric/Manual entry for employees.

### 16. Reports Module (`apps.reports`)

- **Models**: 3
- **Endpoints**: 6
- **Description**: Centralized reporting engine.
- **Key Models**:
  - `GeneratedReport`: Caching layer for heavy PDF reports.
  - `ReportTemplate`: Definitions of available reports.

### 17. Stats Module (`apps.stats`)

- **Models**: 0 (Logic Only)
- **Endpoints**: 25
- **Description**: Aggregation engine providing JSON data for the Dashboard charts (e.g., "Male vs. Female Ratio", "Fee Collection this Month").

---

## 5. Technology Stack Specifications

- **Language**: Python 3.14 (Runtime Environment)
- **Framework**: Django 5.2.9
- **REST Toolkit**: Django Rest Framework (DRF) 3.16.1
- **Documentation**: OpenAPI 3.0 via `drf-spectacular`
- **Database**: PostgreSQL / SQLite (Dev)
- **Task Queue**: Celery (Proposed for async notifications)

This document certifies that the project adheres to modern software engineering practices, prioritizing **scalability**, **maintainability**, and **data integrity**.
