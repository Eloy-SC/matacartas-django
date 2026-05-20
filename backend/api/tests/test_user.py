from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PerfilActualizarAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.user = UserModel.objects.create_user(
            username="alice",
            password="old-password-123",
            email="alice@example.com",
            nombre="Alice",
        )
        self.user.puntuacion = 10
        self.user.imagen = None
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_update_profile_without_password(self):
        url = reverse("perfil-actualizar")
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "nombre": "Alice Updated",
            "imagen": "https://example.com/a.png",
        }

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "alice")
        self.assertEqual(self.user.email, "alice@example.com")
        self.assertEqual(self.user.nombre, "Alice Updated")
        self.assertEqual(self.user.imagen, "https://example.com/a.png")
        self.assertTrue(self.user.check_password("old-password-123"))

    def test_update_profile_changes_password_when_provided(self):
        url = reverse("perfil-actualizar")
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "nombre": "Alice",
            "imagen": None,
            "password": "new-password-123",
        }

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-password-123"))

    def test_update_profile_rejects_existing_username(self):
        UserModel = get_user_model()
        other = UserModel.objects.create_user(
            username="bob",
            password="x",
            email="bob@example.com",
            nombre="Bob",
        )

        url = reverse("perfil-actualizar")
        payload = {
            "username": "bob",
            "email": "alice@example.com",
            "nombre": "Alice",
            "imagen": None,
        }

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_update_profile_rejects_existing_email(self):
        UserModel = get_user_model()
        other = UserModel.objects.create_user(
            username="bob",
            password="x",
            email="bob@example.com",
            nombre="Bob",
        )

        url = reverse("perfil-actualizar")
        payload = {
            "username": "alice",
            "email": "bob@example.com",
            "nombre": "Alice",
            "imagen": None,
        }

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
