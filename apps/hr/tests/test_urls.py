from django.test import SimpleTestCase
from django.urls import reverse


class HRURLTests(SimpleTestCase):
    """Ensure all HR router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'leavetype-list',
            'leaveapplication-list',
            'leaveapproval-list',
            'leavebalance-list',
            'salarystructure-list',
            'salarycomponent-list',
            'deduction-list',
            'payroll-list',
            'payrollitem-list',
            'payslip-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
