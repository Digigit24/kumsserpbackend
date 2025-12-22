from django.test import SimpleTestCase
from django.urls import reverse


class HostelURLTests(SimpleTestCase):
    """Ensure all hostel router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'hostel-list',
            'roomtype-list',
            'room-list',
            'bed-list',
            'hostelallocation-list',
            'hostelfee-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
