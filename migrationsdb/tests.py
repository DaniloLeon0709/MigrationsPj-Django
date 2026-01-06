from django.test import SimpleTestCase
from django.urls import resolve, reverse


class UrlsTests(SimpleTestCase):
    def test_update_genre_api_url_is_registered(self):
        url = reverse('update_genre_api', kwargs={'genre_id': 1})
        match = resolve(url)
        self.assertEqual(match.view_name, 'update_genre_api')
