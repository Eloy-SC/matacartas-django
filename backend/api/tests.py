from django.urls import reverse
from django.contrib.auth.models import User
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


class RegisterAPITest(APITestCase):
    def test_register_creates_user(self):
        url = reverse("register")
        payload = {"username": "alice", "password": "super-secret-123"}

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "alice")
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_register_rejects_existing_username(self):
        User.objects.create_user(username="alice", password="x")

        url = reverse("register")
        payload = {"username": "alice", "password": "another"}

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
