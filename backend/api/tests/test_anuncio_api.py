from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.anuncio import Anuncio


class AnuncioAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="anuncio_api_admin",
            password="pass-123",
            email="anuncio_api_admin@example.com",
            nombre="Admin API",
            is_staff=True,
        )
        self.anuncio = Anuncio.objects.create(
            titulo="Aviso publico",
            subtitulo="Subtitulo",
            descripcion="Descripcion",
            autor=self.admin,
        )

    def test_listar_anuncios_publicos_requires_authentication(self):
        response = self.client.get(reverse("listar-anuncios-publicos"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_anuncio_admin_returns_created(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "titulo": "Nuevo aviso",
            "subtitulo": "Subtitulo nuevo",
            "descripcion": "Descripcion nueva",
        }

        response = self.client.post(reverse("crear-anuncio-admin"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["titulo"], "Nuevo aviso")

    def test_get_anuncio_returns_detail(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse("get-anuncio", args=[self.anuncio.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["descripcion"], "Descripcion")

    def test_publicar_anuncio_returns_published_item(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(reverse("publicar-anuncio-admin", args=[self.anuncio.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["fecha_publicacion"])
