from django.test import SimpleTestCase
from django.urls import reverse


class LibraryURLTests(SimpleTestCase):
    """Ensure all library router endpoints are registered."""

    def test_routes_exist(self):
        route_names = [
            'bookcategory-list',
            'book-list',
            'librarymember-list',
            'librarycard-list',
            'bookissue-list',
            'bookreturn-list',
            'libraryfine-list',
            'bookreservation-list',
        ]
        for name in route_names:
            with self.subTest(name=name):
                self.assertIsNotNone(reverse(name))
