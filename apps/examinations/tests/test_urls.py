from django.test import SimpleTestCase
from django.urls import reverse


class ExaminationsURLTests(SimpleTestCase):
    """Ensure all examinations router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'marksgrade-list',
            'examtype-list',
            'exam-list',
            'examschedule-list',
            'examattendance-list',
            'admitcard-list',
            'marksregister-list',
            'studentmarks-list',
            'examresult-list',
            'progresscard-list',
            'marksheet-list',
            'tabulationsheet-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
