from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.core.models import College
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.reports.models import ReportTemplate, GeneratedReport, SavedReport


class ReportsDummyDataTest(TestCase):
    """Build a dummy reports graph and verify relationships and signals."""

    def setUp(self):
        self.college = College.objects.create(
            code="REP",
            name="Reports College",
            short_name="REP",
            email="info@rep.test",
            phone="9999999994",
            address_line1="123 Reports St",
            city="City",
            state="State",
            pincode="000005",
            country="Testland",
        )
        set_current_college_id(self.college.id)

        self.user = User.objects.create_user(
            username="report_user",
            email="report@rep.test",
            password="dummy-pass",
            first_name="Rep",
            last_name="User",
            college=self.college,
            user_type=UserType.STAFF,
            is_active=True,
        )

        self.template = ReportTemplate.objects.create(
            college=self.college,
            name="Attendance Summary",
            report_type="attendance",
            description="Monthly attendance summary",
            query_params={"month": 6, "year": 2025},
        )
        self.generated = GeneratedReport.objects.create(
            template=self.template,
            generated_by=self.user,
            generation_date=date(2025, 6, 15),
            filters={"class": "10A"},
        )
        self.saved = SavedReport.objects.create(
            user=self.user,
            college=self.college,
            name="Saved Attendance",
            report_type="attendance",
            filters={"month": 6, "year": 2025},
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        self.assertEqual(ReportTemplate.objects.count(), 1)
        self.assertEqual(GeneratedReport.objects.count(), 1)
        self.assertEqual(SavedReport.objects.count(), 1)

        # __str__ calls
        str(self.template)
        str(self.generated)
        str(self.saved)
