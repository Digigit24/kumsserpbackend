from django.test import SimpleTestCase
from django.urls import reverse


class CommunicationURLTests(SimpleTestCase):
    """Ensure all communication router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'notice-list',
            'noticevisibility-list',
            'event-list',
            'eventregistration-list',
            'messagetemplate-list',
            'bulkmessage-list',
            'messagelog-list',
            'notificationrule-list',
            'chatmessage-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
