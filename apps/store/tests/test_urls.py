from django.test import SimpleTestCase
from django.urls import reverse


class StoreURLTests(SimpleTestCase):
    """Ensure all store router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'storecategory-list',
            'storeitem-list',
            'vendor-list',
            'stockreceive-list',
            'storesale-list',
            'saleitem-list',
            'printjob-list',
            'storecredit-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
