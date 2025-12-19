from django.test import SimpleTestCase
from django.urls import reverse


class AccountingURLTests(SimpleTestCase):
    """Ensure all accounting router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'incomecategory-list',
            'expensecategory-list',
            'income-list',
            'expense-list',
            'account-list',
            'voucher-list',
            'financialyear-list',
            'accounttransaction-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
