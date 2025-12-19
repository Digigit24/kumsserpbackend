from django.test import SimpleTestCase
from django.urls import reverse


class StudentURLTests(SimpleTestCase):
    """Ensure all student router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'studentcategory-list',
            'studentgroup-list',
            'student-list',
            'guardian-list',
            'studentguardian-list',
            'studentaddress-list',
            'studentdocument-list',
            'studentmedicalrecord-list',
            'previousacademicrecord-list',
            'studentpromotion-list',
            'certificate-list',
            'studentidcard-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
