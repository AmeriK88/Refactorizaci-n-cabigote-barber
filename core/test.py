from django.test import TestCase
from django.urls import reverse

class SmokeTests(TestCase):
    def test_home_status_code(self):
        # ADJUST NAME IF NEEDED
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
