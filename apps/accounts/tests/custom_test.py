"""
Single-file test suite for Accounts app (models + DRF endpoints).

Assumptions:
- Accounts URLs are included under an API prefix, e.g. /api/v1/accounts/
  If your mount point differs, update BASE_URL.
- CollegeScopedModelViewSet requires X-College-ID header.
- Using DRF and APIClient works (pytest-django + djangorestframework).

If any endpoint path differs, adjust BASE_URL and router paths.
"""

import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient

from apps.core.models import College
from apps.accounts.models import (
    User, UserType,
    Role, UserRole,
    Department, UserProfile
)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

# Change if your urls are mounted elsewhere.
# Example: if urls.py included at path("api/v1/accounts/", include("apps.accounts.urls"))
BASE_URL = ""  # "/api/v1/accounts"  # <-- uncomment and set if needed

USERS = f"{BASE_URL}/users/"
ROLES = f"{BASE_URL}/roles/"
USER_ROLES = f"{BASE_URL}/user-roles/"
DEPARTMENTS = f"{BASE_URL}/departments/"
USER_PROFILES = f"{BASE_URL}/user-profiles/"


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    # Adjust required fields to match your actual College model if needed (tenant_id etc.)
    return College.objects.create(
        code="KUMSS",
        name="KUMSS College",
        short_name="KUMSS",
        email="info@kumss.edu",
        phone="9999999999",
        address_line1="Address 1",
        city="Pune",
        state="MH",
        pincode="411001",
        country="India",
        is_active=True,
    )


@pytest.fixture
def other_college(db):
    return College.objects.create(
        code="OTHER",
        name="Other College",
        short_name="OTHER",
        email="info@other.edu",
        phone="8888888888",
        address_line1="Address 1",
        city="Mumbai",
        state="MH",
        pincode="400001",
        country="India",
        is_active=True,
    )


@pytest.fixture
def admin_user(db, college):
    # Assumes your UserManager supports create_user
    return User.objects.create_user(
        username="admin1",
        email="admin1@kumss.edu",
        password="Test@12345",
        first_name="Admin",
        last_name="One",
        college=college,
        user_type=UserType.COLLEGE_ADMIN,
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def user(db, college):
    return User.objects.create_user(
        username="teacher1",
        email="teacher1@kumss.edu",
        password="Test@12345",
        first_name="Teach",
        last_name="One",
        college=college,
        user_type=UserType.TEACHER,
        is_active=True,
    )


@pytest.fixture
def other_college_user(db, other_college):
    return User.objects.create_user(
        username="teacher2",
        email="teacher2@other.edu",
        password="Test@12345",
        first_name="Teach",
        last_name="Two",
        college=other_college,
        user_type=UserType.TEACHER,
        is_active=True,
    )


@pytest.fixture
def auth_client(api_client, admin_user, college):
    api_client.force_authenticate(user=admin_user)
    api_client.credentials(HTTP_X_COLLEGE_ID=str(college.id))
    return api_client


@pytest.fixture
def role(db, college):
    return Role.objects.create(
        college=college,
        name="HOD",
        code="HOD",
        description="Head of Department",
        permissions={"accounts": {"users": ["read", "write"]}},
        display_order=1,
        is_active=True,
    )


@pytest.fixture
def role_other_college(db, other_college):
    return Role.objects.create(
        college=other_college,
        name="Exam Controller",
        code="EXAM",
        description="Exam role",
        permissions={"exams": {"papers": ["read"]}},
        display_order=1,
        is_active=True,
    )


@pytest.fixture
def department(db, college, admin_user):
    return Department.objects.create(
        college=college,
        code="CS",
        name="Computer Science",
        short_name="CSE",
        hod=admin_user,
        display_order=1,
        is_active=True,
    )


@pytest.fixture
def profile(db, college, user, department):
    return UserProfile.objects.create(
        college=college,
        user=user,
        department=department,
        city="Pune",
        state="MH",
        profile_data={"designation": "Assistant Professor"},
        is_active=True,
    )


# ---------------------------------------------------------------------------
# MODEL TESTS
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_user_full_name_middle_name(user):
    user.middle_name = "M"
    user.save()
    assert user.get_full_name() == "Teach M One"


@pytest.mark.django_db
def test_user_lockout_after_5_failed_attempts(user):
    assert user.is_locked_out() is False
    for _ in range(5):
        user.increment_failed_login()

    user.refresh_from_db()
    assert user.failed_login_attempts >= 5
    assert user.lockout_until is not None
    assert user.is_locked_out() is True


@pytest.mark.django_db
def test_user_reset_failed_login(user):
    user.failed_login_attempts = 5
    user.lockout_until = timezone.now() + timedelta(minutes=10)
    user.save()

    user.reset_failed_login()
    user.refresh_from_db()
    assert user.failed_login_attempts == 0
    assert user.lockout_until is None
    assert user.is_locked_out() is False


@pytest.mark.django_db
def test_userrole_clean_valid(admin_user, user, role, college):
    ur = UserRole(college=college, user=user, role=role, assigned_by=admin_user)
    ur.full_clean()  # should not raise


@pytest.mark.django_db
def test_userrole_clean_user_college_mismatch_raises(admin_user, user, role_other_college, other_college):
    # user belongs to college fixture, assignment is other_college
    ur = UserRole(college=other_college, user=user, role=role_other_college, assigned_by=admin_user)
    with pytest.raises(ValidationError):
        ur.full_clean()


@pytest.mark.django_db
def test_userrole_clean_role_college_mismatch_raises(admin_user, user, role_other_college, college):
    # role belongs to other college, but assignment says college
    ur = UserRole(college=college, user=user, role=role_other_college, assigned_by=admin_user)
    with pytest.raises(ValidationError):
        ur.full_clean()


# ---------------------------------------------------------------------------
# API TESTS - USERS
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_users_list_requires_auth(api_client, college):
    api_client.credentials(HTTP_X_COLLEGE_ID=str(college.id))
    res = api_client.get(USERS)
    assert res.status_code in (401, 403)


@pytest.mark.django_db
def test_users_list(auth_client):
    res = auth_client.get(USERS)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) or "results" in data


@pytest.mark.django_db
def test_users_create(auth_client, college):
    payload = {
        "username": "student1",
        "email": "student1@kumss.edu",
        "first_name": "Stud",
        "last_name": "One",
        "user_type": UserType.STUDENT,
        "college": college.id,
        "password": "Test@12345",
    }
    res = auth_client.post(USERS, payload, format="json")
    assert res.status_code in (201, 200)
    assert User.objects.filter(username="student1").exists()


@pytest.mark.django_db
def test_users_retrieve(auth_client, user):
    res = auth_client.get(f"{USERS}{user.id}/")
    assert res.status_code == 200
    assert res.json().get("id") == str(user.id)


@pytest.mark.django_db
def test_users_update_patch(auth_client, user):
    res = auth_client.patch(f"{USERS}{user.id}/", {"first_name": "Teacher"}, format="json")
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "Teacher"


@pytest.mark.django_db
def test_users_soft_delete(auth_client, user):
    res = auth_client.delete(f"{USERS}{user.id}/")
    assert res.status_code in (204, 200)
    user.refresh_from_db()
    assert user.is_active is False


@pytest.mark.django_db
def test_users_me(auth_client, admin_user):
    res = auth_client.get(f"{USERS}me/")
    assert res.status_code == 200
    assert res.json().get("id") == str(admin_user.id)


@pytest.mark.django_db
def test_users_change_password(auth_client, admin_user):
    payload = {"old_password": "Test@12345", "new_password": "NewPass@12345"}
    res = auth_client.post(f"{USERS}change_password/", payload, format="json")
    assert res.status_code == 200
    admin_user.refresh_from_db()
    assert admin_user.check_password("NewPass@12345") is True
    assert admin_user.last_password_change is not None


@pytest.mark.django_db
def test_users_bulk_activate(auth_client, user):
    payload = {"ids": [str(user.id)], "is_active": False}
    res = auth_client.post(f"{USERS}bulk_activate/", payload, format="json")
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.is_active is False


@pytest.mark.django_db
def test_users_bulk_delete(auth_client, user):
    payload = {"ids": [str(user.id)]}
    res = auth_client.post(f"{USERS}bulk_delete/", payload, format="json")
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.is_active is False


@pytest.mark.django_db
def test_users_bulk_update_type(auth_client, user):
    payload = {"ids": [str(user.id)], "user_type": UserType.STAFF}
    res = auth_client.post(f"{USERS}bulk_update_type/", payload, format="json")
    assert res.status_code == 200
    user.refresh_from_db()
    assert user.user_type == UserType.STAFF


@pytest.mark.django_db
def test_users_by_type(auth_client, user):
    res = auth_client.get(f"{USERS}by-type/{user.user_type}/")
    assert res.status_code == 200


# Optional: college scoping check (depends on your CollegeScopedModelViewSet implementation)
@pytest.mark.django_db
def test_users_college_scoping_blocks_other_college(auth_client, other_college_user):
    """
    If scoping is enforced, admin from College A should not retrieve user from College B.
    Expected: 404 or 403.
    If your implementation allows cross-college, adjust/remove this test.
    """
    res = auth_client.get(f"{USERS}{other_college_user.id}/")
    assert res.status_code in (403, 404)


# ---------------------------------------------------------------------------
# API TESTS - ROLES
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_roles_crud(auth_client, college):
    payload = {
        "college": college.id,
        "name": "Exam Controller",
        "code": "EXAM_CTRL",
        "description": "Exam dept head",
        "permissions": {"exams": {"papers": ["read", "write"]}},
        "display_order": 2,
    }
    res = auth_client.post(ROLES, payload, format="json")
    assert res.status_code in (201, 200)
    role_id = res.json().get("id")

    res = auth_client.get(ROLES)
    assert res.status_code == 200

    res = auth_client.patch(f"{ROLES}{role_id}/", {"description": "Updated"}, format="json")
    assert res.status_code == 200

    res = auth_client.delete(f"{ROLES}{role_id}/")
    assert res.status_code in (204, 200)

    r = Role.objects.get(id=role_id)
    assert r.is_active is False


# ---------------------------------------------------------------------------
# API TESTS - DEPARTMENTS
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_departments_crud(auth_client, college, admin_user):
    payload = {
        "college": college.id,
        "code": "ME",
        "name": "Mechanical Engineering",
        "short_name": "ME",
        "hod": str(admin_user.id),
        "display_order": 1,
    }
    res = auth_client.post(DEPARTMENTS, payload, format="json")
    assert res.status_code in (201, 200)
    dep_id = res.json().get("id")

    res = auth_client.get(DEPARTMENTS)
    assert res.status_code == 200

    res = auth_client.patch(f"{DEPARTMENTS}{dep_id}/", {"name": "Mechanical Engg"}, format="json")
    assert res.status_code == 200

    res = auth_client.delete(f"{DEPARTMENTS}{dep_id}/")
    assert res.status_code in (204, 200)

    d = Department.objects.get(id=dep_id)
    assert d.is_active is False


# ---------------------------------------------------------------------------
# API TESTS - USER ROLES
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_user_roles_crud(auth_client, college, user, role, admin_user):
    payload = {
        "college": college.id,
        "user": str(user.id),
        "role": role.id,
        "assigned_by": str(admin_user.id),
    }
    res = auth_client.post(USER_ROLES, payload, format="json")
    assert res.status_code in (201, 200)
    ur_id = res.json().get("id")

    res = auth_client.get(USER_ROLES)
    assert res.status_code == 200

    res = auth_client.delete(f"{USER_ROLES}{ur_id}/")
    assert res.status_code in (204, 200)

    ur = UserRole.objects.get(id=ur_id)
    assert ur.is_active is False


# ---------------------------------------------------------------------------
# API TESTS - USER PROFILES
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_user_profiles_crud(auth_client, college, user, department):
    payload = {
        "college": college.id,
        "user": str(user.id),
        "department": department.id,
        "city": "Pune",
        "state": "MH",
        "profile_data": {"roll_no": "CS001"},
    }
    res = auth_client.post(USER_PROFILES, payload, format="json")
    assert res.status_code in (201, 200)
    pid = res.json().get("id")

    res = auth_client.get(USER_PROFILES)
    assert res.status_code == 200

    res = auth_client.patch(f"{USER_PROFILES}{pid}/", {"city": "PCMC"}, format="json")
    assert res.status_code == 200

    res = auth_client.delete(f"{USER_PROFILES}{pid}/")
    assert res.status_code in (204, 200)

    p = UserProfile.objects.get(id=pid)
    assert p.is_active is False


@pytest.mark.django_db
def test_user_profiles_me(auth_client):
    # Your code returns 404 if profile not found
    res = auth_client.get(f"{USER_PROFILES}me/")
    assert res.status_code in (200, 404)
