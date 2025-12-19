from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User, UserType


class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="pass1234",
            first_name="Alice",
            last_name="Wonder",
        )

    def test_user_creation_defaults(self):
        self.assertTrue(self.user.pk)
        self.assertEqual(self.user.user_type, UserType.STUDENT)
        self.assertTrue(self.user.is_active)
        self.assertEqual(str(self.user), "Alice Wonder (alice)")

    def test_full_name_with_middle_name(self):
        self.user.middle_name = "Middle"
        self.assertEqual(self.user.get_full_name(), "Alice Middle Wonder")

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username="bob",
                email="",
                password="x",
                first_name="Bob",
                last_name="Builder",
            )

    def test_superuser_flags(self):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
            first_name="Super",
            last_name="Admin",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.user_type, UserType.SUPER_ADMIN)

    def test_lockout_logic(self):
        self.user.failed_login_attempts = 4
        self.user.save()
        self.user.increment_failed_login()
        self.user.refresh_from_db()
        self.assertGreaterEqual(self.user.failed_login_attempts, 5)
        self.assertIsNotNone(self.user.lockout_until)
        # After lockout time passes, is_locked_out should flip; simulate by moving time back
        self.user.lockout_until = timezone.now() - timedelta(minutes=1)
        self.assertFalse(self.user.is_locked_out())
