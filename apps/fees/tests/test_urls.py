from django.test import SimpleTestCase
from django.urls import reverse


class FeesURLTests(SimpleTestCase):
    """Ensure all fees router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'feegroup-list',
            'feetype-list',
            'feemaster-list',
            'feestructure-list',
            'feediscount-list',
            'studentfeediscount-list',
            'feecollection-list',
            'feereceipt-list',
            'feeinstallment-list',
            'feefine-list',
            'feerefund-list',
            'bankpayment-list',
            'onlinepayment-list',
            'feereminder-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
