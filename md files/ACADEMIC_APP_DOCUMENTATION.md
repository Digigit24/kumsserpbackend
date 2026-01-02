# KUMSS ERP - Academic Module Documentation

**Module:** `apps.academic`  
**Version:** 1.0.0  
**Status:** Official Technical Reference  
**Last Updated:** 2026-01-01

---

## 1. Executive Summary

The **Academic Module** is the foundational core of the KUMSS ERP system. It defines the structural and operational framework for educational delivery. It manages the institutional hierarchy (Faculties, Programs), the physical infrastructure (Classrooms), and the temporal mapping (Timetables, Class Times) required to run an academic institution.

The module is engineered for **High-Concomitant Multi-Tenancy**, ensuring that multiple colleges can operate on the same database while maintaining strict data isolation.

---

## 2. Core Architecture Principles

### 2.1 Multi-Tenancy & Scoping

Most models in this module inherit from `CollegeScopedModel`.

- **Automatic Filtering**: Every query is automatically scoped to the `college_id` provided in the request header (`X-College-ID`).
- **Data Integrity**: Unique constraints are composite, including the `college` field (e.g., a Faculty code "CSE" can exist in College A and College B simultaneously).

### 2.2 Audit & Record Keeping

- **Audit Logging**: Inherits from `AuditModel`, providing `created_at`, `updated_at`, `created_by`, and `updated_by` fields automatically.
- **Soft Deletion**: Records are never hard-deleted. Instead, they use a soft-delete mechanism (`is_active=False`) to preserve historical academic data and relationships.

---

## 3. Detailed Model Breakdown

### 3.1 Organization Hierarchy

#### `Faculty` (Department)

Represents a major division within the college.

- **Key Fields**: `code`, `name`, `hod` (Linked to User), `display_order`.
- **Logic**: Serves as the parent container for Academic Programs.

#### `Program` (Degree/Course)

Represents a specific degree or course of study.

- **Key Fields**: `faculty`, `program_type` (UG/PG/Diploma), `duration`, `duration_type` (Semester/Year).
- **Logic**: Defines the standard timeline and credit requirements for students.

#### `Class`

A specific instance of a Program for a particular session and semester.

- **Key Fields**: `program`, `academic_session`, `semester`, `year`.
- **Constraint**: Unique combination of `college`, `program`, `session`, and `semester`.

#### `Section`

The smallest group of students within a Class.

- **Key Fields**: `class_obj`, `name`, `max_students`.

### 3.2 Academic Delivery

#### `Subject` (Course)

The master repository of all courses offered by the college.

- **Key Fields**: `code`, `subject_type` (Theory/Practical), `credits`, `max_marks`, `pass_marks`.

#### `SubjectAssignment` **(The Bridge)**

A critical model that maps teachers to specific academic delivery units.

- **Relationships**: `Subject` + `Class` + `Section` + `Teacher` + `Lab Instructor`.
- **Purpose**: This is the source of truth for "Who is teaching what."

#### `OptionalSubject`

Handles groups of elective subjects where students can choose from a pool.

- **Logic**: Defines `min_selection` and `max_selection` rules.

### 3.3 Infrastructure & Scheduling

#### `Classroom`

Physical or virtual locations.

- **Key Fields**: `room_type`, `capacity`, `building`, `facilities` (AC, Projector).

#### `ClassTime` (Periods)

Defines the slots in a daily schedule.

- **Key Fields**: `period_number`, `start_time`, `end_time`, `is_break`.

#### `Timetable`

The master weekly schedule.

- **Relationships**: `Section` + `SubjectAssignment` + `ClassTime` + `Classroom`.
- **Logic**: Maps a 3D matrix of Time, Space, and Resource (Teacher/Subject).

#### `LabSchedule`

Specialized scheduling for laboratory sessions, supporting batch-wise division of sections.

---

## 4. Operational Workflows

### 4.1 Initial Institutional Setup

1. Define **Faculties** (e.g., School of Engineering).
2. Create **Programs** under each Faculty (e.g., Computer Science).
3. Register **Subjects** in the college repository.

### 4.2 Ongoing Session Management

1. Initialize **Classes** for the new `AcademicSession`.
2. Generate **Sections** for each Class.
3. Perform **Subject Assignments**: Assign teachers to each Subject-Section pair.

### 4.3 Daily Operations (Scheduling)

1. Define **Class Times** (Period 1 to Period N).
2. Register **Classrooms**.
3. Build the **Timetable**: Assign SubjectAssignments to time slots and rooms.

---

## 5. API & Integration Reference

### 5.1 Key Endpoints

| Endpoint                             | Method   | Purpose                         |
| :----------------------------------- | :------- | :------------------------------ |
| `/api/academic/faculties/`           | GET/POST | Manage departments              |
| `/api/academic/subject-assignments/` | GET/POST | View/Create teaching duties     |
| `/api/academic/timetable/`           | GET/POST | Master schedule access          |
| `/api/academic/classes/`             | GET      | List classes by program/session |

### 5.2 Dynamic Filtering

All list endpoints support advanced filtering:

- **Search**: Search by name or code across all models.
- **Hierarchical Filter**: Filter classes by `program`, sections by `class_obj`, etc.
- **Active Only**: Default behavior returns only `is_active=True` records.

---

## 6. Technical Implementation Details

- **Custom Managers**: The module uses `all_colleges()` to bypass multi-tenancy filters for superadmin views and `all()` for scoped views.
- **Nested Serializers**: Serializers like `TimetableSerializer` provide full depth (showing Subject names and Teacher details) to minimize frontend API calls.
- **Conflict Prevention**: Unique constraints on Timetable prevent overbooking of Classrooms or Teachers at the same `ClassTime` and `day_of_week`.

---

_End of Documentation_
