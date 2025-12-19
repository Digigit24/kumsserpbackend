from django.test import SimpleTestCase
from django.urls import reverse


class TeacherURLTests(SimpleTestCase):
    """Ensure all teacher router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'teacher-list',
            'studymaterial-list',
            'assignment-list',
            'assignmentsubmission-list',
            'homework-list',
            'homeworksubmission-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
