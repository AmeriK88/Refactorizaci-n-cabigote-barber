# core/tests.py
from django.test import TestCase
from django.urls import reverse

class SmokeTests(TestCase):
    def test_home_status_code(self):
        # Ajusta el name si tu home no se llama "home"
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
