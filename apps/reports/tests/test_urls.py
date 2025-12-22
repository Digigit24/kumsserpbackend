from django.test import SimpleTestCase
from django.urls import reverse


class ReportsURLTests(SimpleTestCase):
    """Ensure all reports router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'reporttemplate-list',
            'generatedreport-list',
            'savedreport-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
