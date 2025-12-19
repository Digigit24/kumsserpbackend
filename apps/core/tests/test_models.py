from django.test import TestCase

from apps.core.models import College


class CollegeModelTest(TestCase):
    def test_create_and_str(self):
        college = College.objects.create(
            code="TECH01",
            name="Tech University",
            short_name="TechU",
            email="info@techu.edu",
            phone="1234567890",
            address_line1="123 Main St",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001",
            country="India",
            is_main=True,
        )

        self.assertTrue(college.pk)
        self.assertEqual(str(college), "Tech University (TECH01)")
