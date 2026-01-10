# Role Seeding Guide

## Problem
The organizational hierarchy tree was not displaying all roles (like Students) because roles must be **defined in the database** for each college. Simply having users with `user_type='student'` is not enough - you need actual Role entries.

## Solution
Use the `seed_college_roles` management command to create common roles for all your colleges.

## Usage

### Seed roles for ALL colleges:
```bash
python manage.py seed_college_roles
```

### Seed roles for a SPECIFIC college:
```bash
python manage.py seed_college_roles --college-id 1
```

## What roles are created?

The command creates the following roles for each college:

1. **Student** (level 10) - Students enrolled in the college
2. **Teacher** (level 5) - Teaching staff members
3. **HOD** (level 4) - Head of Department
4. **Principal** (level 2) - College Principal/Head
5. **Staff** (level 7) - Non-teaching staff members
6. **Store Manager** (level 6) - Store operations management
7. **Librarian** (level 7) - Library management staff
8. **Accountant** (level 6) - Accounts and finance
9. **Lab Assistant** (level 8) - Laboratory technical assistant

## After running the command

Once you run this command, all these roles will appear in your organizational hierarchy tree with their respective counts, including:
- `/api/core/organization/nodes/tree/` - Full tree structure
- `/api/core/organization/nodes/roles_summary/` - Summary with counts

## Example Output

Before seeding:
```
KUMSS Engineering College
├── Store Manager (count: 1)
└── Teacher (count: 5)
```

After seeding:
```
KUMSS Engineering College
├── Principal (count: 1)
├── HOD (count: 3)
├── Teacher (count: 5)
├── Store Manager (count: 1)
├── Librarian (count: 0)
├── Staff (count: 2)
├── Lab Assistant (count: 0)
├── Accountant (count: 0)
└── Student (count: 150)  ← NOW VISIBLE!
```

## Notes

- The command uses `update_or_create`, so it's safe to run multiple times
- Existing roles will be updated, new ones will be created
- Role counts are automatically calculated from:
  - `HierarchyUserRole` assignments
  - `AccountUserRole` assignments
  - User `user_type` field matching role `code`
- All roles show with their counts (even if 0)
