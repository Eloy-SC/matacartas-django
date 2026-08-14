from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.partida import Partida


class TicketAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.user = UserModel.objects.create_user(
            username="ticket_api_user",
            password="ticket-pass-123",
            email="ticket_api_user@example.com",
            nombre="Ticket API User",
        )

        self.partida = Partida.objects.create(
            nombre="PartidaTicketAPI",
            num_jugadores=2,
            privada=False,
            clave=None,
            longitud=Partida.LongitudPartida.NORMAL,
            cartas_especiales=True,
            tickets=True,
            tiempo_max_turno=90,
        )

    def test_usar_ticket_requires_authentication(self):
        url = reverse("usar-ticket", args=[self.partida.id])

        response = self.client.put(url, {"ticket": "ticket_cp_2"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("api.views.ticket_view.notificar_mesa_actualizada")
    @patch("api.views.ticket_view.ticket_service.usar_ticket")
    def test_usar_ticket_returns_200_and_calls_service(self, service_mock, notify_mock):
        url = reverse("usar-ticket", args=[self.partida.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.put(url, {"ticket": "ticket_cp_2"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_mock.assert_called_once_with(self.user, self.partida.id, "ticket_cp_2")
        notify_mock.assert_called_once_with(self.partida.id)

    @patch("api.views.ticket_view.ticket_service.usar_ticket", side_effect=PermissionError("No participas"))
    def test_usar_ticket_returns_403_on_permission_error(self, _service_mock):
        url = reverse("usar-ticket", args=[self.partida.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.put(url, {"ticket": "ticket_cp_2"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    @patch("api.views.ticket_view.ticket_service.usar_ticket", side_effect=ValueError("Ticket no reconocido"))
    def test_usar_ticket_returns_404_on_value_error(self, _service_mock):
        url = reverse("usar-ticket", args=[self.partida.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.put(url, {"ticket": "ticket_invalido"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_usar_ticket_returns_400_when_ticket_missing(self):
        url = reverse("usar-ticket", args=[self.partida.id])
        self.client.force_authenticate(user=self.user)

        response = self.client.put(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("detail"), "No se proporcionó el ticket a usar.")
