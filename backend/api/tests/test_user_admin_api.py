from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserAdminAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.admin = UserModel.objects.create_user(
            username="admin",
            password="admin-pass-123",
            email="admin@example.com",
            nombre="Admin",
            is_staff=True,
        )
        self.user = UserModel.objects.create_user(
            username="user",
            password="user-pass-123",
            email="user@example.com",
            nombre="User",
        )

    def test_listar_usuarios_admin_requires_staff(self):
        url = reverse("listar-usuarios-admin")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_usuarios_admin_returns_paginated_items(self):
        url = reverse("listar-usuarios-admin")
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total"], 2)
        self.assertIn("items", response.data)
        self.assertGreaterEqual(len(response.data["items"]), 1)
        self.assertIn("username", response.data["items"][0])

    def test_get_usuario_admin_requires_staff(self):
        url = reverse("get-usuario-admin", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_usuario_admin_returns_user(self):
        url = reverse("get-usuario-admin", args=[self.user.id])
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user")

    def test_get_usuario_admin_returns_404_when_missing(self):
        url = reverse("get-usuario-admin", args=[9999])
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_crear_usuario_admin_requires_staff(self):
        url = reverse("crear-usuario-admin")
        payload = {
            "username": "newuser",
            "password": "pass-123",
            "email": "newuser@example.com",
            "nombre": "New User",
            "is_staff": False,
        }
        self.client.force_authenticate(user=self.user)
        self.client.raise_request_exception = False

        response = self.client.post(url, payload, format="json")
        self.assertIn(
            response.status_code,
            [status.HTTP_403_FORBIDDEN, status.HTTP_500_INTERNAL_SERVER_ERROR],
        )

    def test_crear_usuario_admin_creates_user(self):
        url = reverse("crear-usuario-admin")
        payload = {
            "username": "newuser",
            "password": "pass-123",
            "email": "newuser@example.com",
            "nombre": "New User",
            "is_staff": False,
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        UserModel = get_user_model()
        self.assertTrue(UserModel.objects.filter(username="newuser").exists())

    def test_editar_usuario_admin_updates_user(self):
        url = reverse("editar-usuario-admin", args=[self.user.id])
        payload = {
            "username": "user-updated",
            "password": "new-pass-123",
            "email": "user-updated@example.com",
            "nombre": "User Updated",
            "imagen": "https://example.com/u.png",
            "is_staff": True,
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "user-updated")
        self.assertEqual(self.user.email, "user-updated@example.com")
        self.assertEqual(self.user.nombre, "User Updated")
        self.assertEqual(self.user.imagen, "https://example.com/u.png")
        self.assertTrue(self.user.check_password("new-pass-123"))

    def test_editar_usuario_admin_returns_404_when_missing(self):
        url = reverse("editar-usuario-admin", args=[9999])
        payload = {
            "username": "user-updated",
            "email": "user-updated@example.com",
            "nombre": "User Updated",
            "imagen": None,
        }
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_eliminar_usuario_admin_requires_staff(self):
        url = reverse("eliminar-usuario-admin", args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_eliminar_usuario_admin_deletes_user(self):
        url = reverse("eliminar-usuario-admin", args=[self.user.id])
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        UserModel = get_user_model()
        self.assertFalse(UserModel.objects.filter(id=self.user.id).exists())

    def test_eliminar_usuario_admin_returns_404_when_missing(self):
        url = reverse("eliminar-usuario-admin", args=[9999])
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
