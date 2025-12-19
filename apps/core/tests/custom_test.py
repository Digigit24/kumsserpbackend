from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date

from apps.core.models import (
    College,
    AcademicYear,
    AcademicSession,
    Holiday,
    Weekend,
    SystemSetting,
    NotificationSetting,
    ActivityLog
)

User = get_user_model()


# =========================================================
# BASE SETUP
# =========================================================

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
        )

        self.college = College.objects.create(
            code="KUMS01",
            name="KUMS Engineering College",
            short_name="KUMS",
            email="info@kums.edu",
            phone="9999999999",
            address_line1="Main Road",
            city="Pune",
            state="MH",
            pincode="411001",
            created_by=self.user
        )


# =========================================================
# COLLEGE MODEL
# =========================================================

class CollegeModelTest(BaseTestCase):

    def test_college_creation(self):
        self.assertEqual(self.college.code, "KUMS01")
        self.assertTrue(self.college.is_active)

    def test_college_str(self):
        self.assertEqual(
            str(self.college),
            "KUMS Engineering College (KUMS01)"
        )

    def test_soft_delete_and_restore(self):
        self.college.soft_delete()
        self.assertFalse(self.college.is_active)

        self.college.restore()
        self.assertTrue(self.college.is_active)


# =========================================================
# ACADEMIC YEAR
# =========================================================

class AcademicYearTest(BaseTestCase):

    def test_academic_year_creation(self):
        year = AcademicYear.objects.create(
            college=self.college,
            year="2025-2026",
            start_date=date(2025, 6, 1),
            end_date=date(2026, 5, 31),
            is_current=True
        )

        self.assertEqual(year.year, "2025-2026")
        self.assertTrue(year.is_current)

    def test_invalid_academic_year_dates(self):
        year = AcademicYear(
            college=self.college,
            year="2025-2026",
            start_date=date(2026, 1, 1),
            end_date=date(2025, 1, 1),
        )

        with self.assertRaises(ValidationError):
            year.full_clean()


# =========================================================
# ACADEMIC SESSION
# =========================================================

class AcademicSessionTest(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.year = AcademicYear.objects.create(
            college=self.college,
            year="2025-2026",
            start_date=date(2025, 6, 1),
            end_date=date(2026, 5, 31),
        )

    def test_session_creation(self):
        session = AcademicSession.objects.create(
            college=self.college,
            academic_year=self.year,
            name="Semester 1",
            semester=1,
            start_date=date(2025, 6, 15),
            end_date=date(2025, 11, 30),
            is_current=True
        )

        self.assertEqual(session.semester, 1)
        self.assertTrue(session.is_current)

    def test_invalid_semester(self):
        session = AcademicSession(
            college=self.college,
            academic_year=self.year,
            name="Invalid",
            semester=10,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 5, 1),
        )

        with self.assertRaises(ValidationError):
            session.full_clean()


# =========================================================
# HOLIDAY
# =========================================================

class HolidayTest(BaseTestCase):

    def test_holiday_creation(self):
        holiday = Holiday.objects.create(
            college=self.college,
            name="Independence Day",
            date=date(2025, 8, 15),
            holiday_type="national"
        )

        self.assertEqual(holiday.holiday_type, "national")


# =========================================================
# WEEKEND
# =========================================================

class WeekendTest(BaseTestCase):

    def test_weekend_creation(self):
        # Defaults created via signal on College post_save (Saturday/Sunday)
        weekend = Weekend.objects.all_colleges().get(
            college=self.college,
            day=6,  # Sunday
        )
        self.assertEqual(weekend.day, 6)


# =========================================================
# SYSTEM SETTINGS
# =========================================================

class SystemSettingTest(BaseTestCase):

    def test_system_setting_creation(self):
        setting = SystemSetting.objects.create(
            college=self.college,
            settings={
                "attendance": True,
                "fees": False
            }
        )

        self.assertTrue(setting.settings["attendance"])


# =========================================================
# NOTIFICATION SETTINGS
# =========================================================

class NotificationSettingTest(BaseTestCase):

    def test_notification_settings(self):
        notif = NotificationSetting.objects.create(
            college=self.college,
            sms_enabled=True,
            email_enabled=True,
            whatsapp_enabled=False
        )

        self.assertTrue(notif.sms_enabled)
        self.assertTrue(notif.email_enabled)
        self.assertFalse(notif.whatsapp_enabled)


# =========================================================
# ACTIVITY LOG
# =========================================================

class ActivityLogTest(BaseTestCase):

    def test_activity_log_creation(self):
        log = ActivityLog.objects.create(
            user=self.user,
            college=self.college,
            action="create",
            model_name="College",
            description="College created"
        )

        self.assertEqual(log.action, "create")
        self.assertEqual(log.model_name, "College")
