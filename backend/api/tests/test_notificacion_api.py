from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.notificacion import SolicitudAmistad


class NotificacionAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.sender = User.objects.create_user(
            username="notificacion_api_sender",
            password="pass-123",
            email="sender_api@example.com",
            nombre="Emisor API",
        )
        self.receiver = User.objects.create_user(
            username="notificacion_api_receiver",
            password="pass-123",
            email="receiver_api@example.com",
            nombre="Receptor API",
        )
        SolicitudAmistad.objects.create(emisor=self.sender, receptor=self.receiver)

    def test_listar_notificaciones_requires_authentication(self):
        response = self.client.get(reverse("listar-notificaciones"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_notificaciones_returns_request(self):
        self.client.force_authenticate(user=self.receiver)

        response = self.client.get(reverse("listar-notificaciones"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"][0]["tipo"], "solicitud_amistad")
        self.assertEqual(response.data["items"][0]["emisor_nombre"], "Emisor API")

    def test_aceptar_solicitud_creates_friendship(self):
        solicitud = SolicitudAmistad.objects.get(receptor=self.receiver)
        self.client.force_authenticate(user=self.receiver)

        response = self.client.post(reverse("aceptar-solicitud-amistad", args=[solicitud.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_rechazar_solicitud_removes_notification(self):
        solicitud = SolicitudAmistad.objects.get(receptor=self.receiver)
        self.client.force_authenticate(user=self.receiver)

        response = self.client.delete(reverse("rechazar-solicitud-amistad", args=[solicitud.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SolicitudAmistad.objects.filter(id=solicitud.id).exists())
