from django.test import SimpleTestCase
from django.urls import reverse


class OnlineExamURLTests(SimpleTestCase):
    """Ensure all online exam router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'questionbank-list',
            'question-list',
            'questionoption-list',
            'onlineexam-list',
            'examquestion-list',
            'studentexamattempt-list',
            'studentanswer-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
