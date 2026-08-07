from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.mano import Mano
from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.models.ronda import Ronda


class ManoAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.creator = UserModel.objects.create_user(
            username="creator",
            password="creator-pass-123",
            email="creator@example.com",
            nombre="Creator",
        )
        self.player = UserModel.objects.create_user(
            username="player",
            password="player-pass-123",
            email="player@example.com",
            nombre="Player",
        )
        self.outsider = UserModel.objects.create_user(
            username="outsider",
            password="outsider-pass-123",
            email="outsider@example.com",
            nombre="Outsider",
        )

        self.partida = Partida.objects.create(
            nombre="PartidaManoApi",
            num_jugadores=2,
            privada=False,
            clave=None,
            longitud=Partida.LongitudPartida.NORMAL,
            cartas_especiales=True,
            tickets=True,
            tiempo_max_turno=90,
            disposicion_jugadores=[PartidaUsuario.ColorJugador.ROJO, PartidaUsuario.ColorJugador.AZUL],
            turno_actual=PartidaUsuario.ColorJugador.ROJO,
        )
        self.pu_creator = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.creator,
            creador=True,
            listo=True,
            color=PartidaUsuario.ColorJugador.ROJO,
            cartas=["MONEDERO_PECULIAR", "CARTA_B", "CARTA_C", "CARTA_D"],
        )
        self.pu_player = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.player,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.AZUL,
            cartas=[],
        )
        self.mano = Mano.objects.create(partida=self.partida, num=1)
        self.ronda = Ronda.objects.create(mano=self.mano, num=0, cartas={}, cambios=0)

    def test_get_mesa_returns_data(self):
        url = reverse("get-mesa", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["partida"]["partida_id"], self.partida.id)
        self.assertEqual(response.data["jugador"]["nombre"], "Creator")

    def test_get_mesa_returns_403_for_non_member(self):
        url = reverse("get-mesa", args=[self.partida.id])
        self.client.force_authenticate(user=self.outsider)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("api.views.mano_view.notificar_mesa_actualizada")
    @patch("api.views.mano_view.mano_service.repartir_cartas")
    def test_repartir_cartas_returns_200(self, repartir_mock, _notify_mock):
        url = reverse("repartir-cartas", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        repartir_mock.assert_called_once_with(self.creator, self.partida.id)

    @patch("api.views.mano_view.notificar_mesa_actualizada")
    @patch("api.views.mano_view.mano_service.jugador_quiere_cambiar")
    def test_jugador_quiere_cambiar_returns_200(self, service_mock, _notify_mock):
        url = reverse("jugador-quiere-cambiar", args=[self.partida.id])
        self.client.force_authenticate(user=self.player)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_mock.assert_called_once_with(self.player, self.partida.id)

    @patch("api.views.mano_view.notificar_mesa_actualizada")
    @patch("api.views.mano_view.mano_service.jugador_no_quiere_cambiar")
    def test_jugador_no_quiere_cambiar_returns_200(self, service_mock, _notify_mock):
        url = reverse("jugador-no-quiere-cambiar", args=[self.partida.id])
        self.client.force_authenticate(user=self.player)

        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_mock.assert_called_once_with(self.player, self.partida.id)

    @patch("api.views.mano_view.notificar_mesa_actualizada")
    @patch("api.views.mano_view.mano_service.cambiar_cartas")
    def test_cambiar_cartas_returns_200(self, service_mock, _notify_mock):
        url = reverse("cambiar-cartas", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.put(url, {"cartas": ["MONEDERO_PECULIAR"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_mock.assert_called_once_with(self.creator, self.partida.id, ["MONEDERO_PECULIAR"])

    @patch("api.views.mano_view.notificar_mesa_actualizada")
    @patch("api.views.mano_view.mano_service.elegir_carta_comodin")
    def test_elegir_carta_comodin_returns_200(self, service_mock, _notify_mock):
        url = reverse("elegir-carta-comodin", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.put(url, {"carta_comodin": "MONEDERO_PECULIAR"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_mock.assert_called_once_with(self.creator, self.partida.id, "MONEDERO_PECULIAR")

    def test_get_datos_carta_returns_values(self):
        url = reverse("get-datos-carta", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.get(url, {"carta": "2_OROS"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "2_OROS")

    @patch("api.views.mano_view.notificar_mesa_actualizada")
    @patch("api.views.mano_view.mano_service.siguiente_mano")
    def test_siguiente_mano_returns_200(self, service_mock, _notify_mock):
        url = reverse("siguiente-mano", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_mock.assert_called_once_with(self.creator, self.partida.id)
