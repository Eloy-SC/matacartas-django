from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.amistad import Amistad


class AmistadAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="amistad_api_user",
            password="pass-123",
            email="amistad_api_user@example.com",
            nombre="Usuario API",
        )
        self.friend = User.objects.create_user(
            username="amistad_api_friend",
            password="pass-123",
            email="amistad_api_friend@example.com",
            nombre="Amigo API",
        )
        Amistad.objects.create(usuario1=self.user, usuario2=self.friend)

    def test_listar_amigos_requires_authentication(self):
        response = self.client.get(reverse("listar-amigos"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_amigos_returns_friend(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("listar-amigos"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"][0]["nombre"], "Amigo API")

    def test_listar_amigos_supports_search(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("listar-amigos"), {"search": "Amigo"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)

    def test_eliminar_amigo_returns_no_content(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(reverse("eliminar-amigo", args=[self.friend.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Amistad.objects.exists())
