from django.test import SimpleTestCase
from django.urls import reverse


class AcademicURLTests(SimpleTestCase):
    """Ensure all academic router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'faculty-list',
            'program-list',
            'class-list',
            'section-list',
            'subject-list',
            'optionalsubject-list',
            'subjectassignment-list',
            'classroom-list',
            'classtime-list',
            'timetable-list',
            'labschedule-list',
            'classteacher-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
