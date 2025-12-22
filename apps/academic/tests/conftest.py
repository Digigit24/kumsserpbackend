import pytest
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.core.models import College, AcademicYear, AcademicSession
from apps.academic.models import Faculty, Program, Class


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def college(db):
    return College.objects.create(
        code="ACAD",
        name="Academic College",
        short_name="ACAD",
        email="acad@example.com",
        phone="1234567890",
        address_line1="Line 1",
        city="City",
        state="State",
        pincode="000000",
        country="Country",
        is_active=True,
    )


@pytest.fixture
def other_college(db):
    return College.objects.create(
        code="ACAD2",
        name="Academic College 2",
        short_name="ACAD2",
        email="acad2@example.com",
        phone="1234567891",
        address_line1="Line 1",
        city="City",
        state="State",
        pincode="000001",
        country="Country",
        is_active=True,
    )


@pytest.fixture
def other_admin_user(db, other_college):
    User = get_user_model()
    return User.objects.create_user(
        username="admin-acad2",
        email="admin2@acad.test",
        password="Test@12345",
        first_name="Admin",
        last_name="Two",
        college=other_college,
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def admin_user(db, college):
    User = get_user_model()
    return User.objects.create_user(
        username="admin-acad",
        email="admin@acad.test",
        password="Test@12345",
        first_name="Admin",
        last_name="Acad",
        college=college,
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def superuser(db, college):
    User = get_user_model()
    return User.objects.create_superuser(
        username="super-acad",
        email="super@acad.test",
        password="Test@12345",
        first_name="Super",
        last_name="User",
        college=college,
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )


@pytest.fixture
def teacher_user(db, college):
    User = get_user_model()
    return User.objects.create_user(
        username="teacher-acad",
        email="teacher@acad.test",
        password="Test@12345",
        first_name="Teach",
        last_name="Acad",
        college=college,
        is_staff=False,
        is_active=True,
    )


@pytest.fixture
def academic_year(db, college):
    return AcademicYear.objects.create(
        college=college,
        year="2024-2025",
        start_date=date(2024, 6, 1),
        end_date=date(2025, 5, 31),
        is_current=True,
    )


@pytest.fixture
def academic_session(db, college, academic_year):
    return AcademicSession.objects.create(
        college=college,
        academic_year=academic_year,
        name="Sem 1",
        semester=1,
        start_date=date(2024, 6, 1),
        end_date=date(2024, 11, 30),
        is_current=True,
    )


@pytest.fixture
def faculty(db, college, admin_user):
    return Faculty.objects.create(
        college=college,
        code="ENG",
        name="Engineering",
        short_name="ENG",
        hod=admin_user,
        display_order=1,
        is_active=True,
    )


@pytest.fixture
def program(db, college, faculty):
    return Program.objects.create(
        college=college,
        faculty=faculty,
        code="BTECH",
        name="B.Tech",
        short_name="BTECH",
        program_type="ug",
        duration=4,
        duration_type="year",
        total_credits=160,
        display_order=1,
        is_active=True,
    )


@pytest.fixture
def class_obj(db, college, program, academic_session):
    return Class.objects.create(
        college=college,
        program=program,
        academic_session=academic_session,
        name="BTECH-1",
        semester=1,
        year=1,
        max_students=60,
        is_active=True,
    )


@pytest.fixture
def auth_client(api_client, admin_user, college):
    api_client.force_authenticate(user=admin_user)
    api_client.credentials(HTTP_X_COLLEGE_ID=str(college.id))
    return api_client


@pytest.fixture
def auth_client_other(api_client, admin_user, other_college):
    api_client.force_authenticate(user=admin_user)
    api_client.credentials(HTTP_X_COLLEGE_ID=str(other_college.id))
    return api_client


@pytest.fixture
def auth_client_other_admin(api_client, other_admin_user, other_college):
    api_client.force_authenticate(user=other_admin_user)
    api_client.credentials(HTTP_X_COLLEGE_ID=str(other_college.id))
    return api_client
