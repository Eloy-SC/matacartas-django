from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status


class RegisterAPITest(APITestCase):
    def test_register_creates_user(self):
        url = reverse("register")
        payload = {
            "username": "alice",
            "password": "super-secret-123",
            "email": "alice@example.com",
            "nombre": "Alice",
            "imagen": None,
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "alice")
        UserModel = get_user_model()
        self.assertTrue(UserModel.objects.filter(username="alice").exists())
        user = UserModel.objects.get(username="alice")
        self.assertEqual(user.nombre, "Alice")

    def test_register_saves_img_in_profile(self):
        url = reverse("register")
        payload = {
            "username": "bob",
            "password": "super-secret-123",
            "password2": "super-secret-123",
            "email": "bob@example.com",
            "nombre": "Bob",
            "imagen": "https://example.com/img.png",
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        UserModel = get_user_model()
        user = UserModel.objects.get(username="bob")
        self.assertEqual(user.imagen, "https://example.com/img.png")

    def test_register_rejects_existing_username(self):
        UserModel = get_user_model()
        UserModel.objects.create_user(username="alice", password="x", nombre="Alice", email="")

        url = reverse("register")
        payload = {
            "username": "alice",
            "password": "another",
            "email": "alice2@example.com",
            "nombre": "Alice2",
            "imagen": None,
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)


