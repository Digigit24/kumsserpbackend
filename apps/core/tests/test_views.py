from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User


class CollegeViewSetTest(APITestCase):
    def setUp(self):
        # Superuser can use X-College-ID: all to bypass scoping
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="pass1234",
        )
        self.client.force_authenticate(self.admin)
        self.headers = {"HTTP_X_COLLEGE_ID": "all"}
        self.list_url = reverse("core:college-list")

    def test_list_empty(self):
        resp = self.client.get(self.list_url, **self.headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)

    def test_create_and_list(self):
        payload = {
            "code": "TECH01",
            "name": "Tech University",
            "short_name": "TechU",
            "email": "info@techu.edu",
            "phone": "1234567890",
            "address_line1": "123 Main St",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560001",
            "country": "India",
            "is_main": True,
        }

        create_resp = self.client.post(
            self.list_url, payload, format="json", **self.headers
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED, create_resp.data)

        list_resp = self.client.get(self.list_url, **self.headers)
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(list_resp.data["count"], 1)
        self.assertEqual(list_resp.data["results"][0]["code"], "TECH01")
