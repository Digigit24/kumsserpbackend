from django.test import SimpleTestCase
from django.urls import reverse


class AttendanceURLTests(SimpleTestCase):
    """Ensure all attendance router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'studentattendance-list',
            'subjectattendance-list',
            'staffattendance-list',
            'attendancenotification-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
