from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class HealthCheckAPITest(APITestCase):
    def test_health_check_returns_200(self):
        url = reverse("health-check")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health_check_returns_expected_data(self):
        url = reverse("health-check")
        response = self.client.get(url)
        self.assertEqual(response.data["status"], "ok")
