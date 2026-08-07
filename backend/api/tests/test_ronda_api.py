from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.mano import Mano
from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.models.ronda import Ronda


class RondaAPITest(APITestCase):
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

        self.partida = Partida.objects.create(
            nombre="PartidaRondaApi",
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
            cartas=["CARTA_A", "CARTA_B", "CARTA_C", "CARTA_D"],
        )
        self.pu_player = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.player,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.AZUL,
            cartas=["CARTA_E", "CARTA_F", "CARTA_G", "CARTA_H"],
        )
        self.mano = Mano.objects.create(partida=self.partida, num=1)
        self.ronda = Ronda.objects.create(mano=self.mano, num=1, cartas={}, cambios=2)

    def test_jugar_carta_requires_payload(self):
        url = reverse("jugar-carta", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("api.views.ronda_view.notificar_mesa_actualizada")
    @patch("api.views.ronda_view.mano_service.get_mano_actual")
    @patch("api.views.ronda_view.ronda_service.jugar_carta")
    def test_jugar_carta_returns_200(self, service_mock, _mano_mock, _notify_mock):
        service_mock.return_value = False
        url = reverse("jugar-carta", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.put(url, {"carta": "CARTA_A"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        service_mock.assert_called_once_with(self.creator, self.partida.id, "CARTA_A")

    @patch("api.views.ronda_view.notificar_mano_finalizada")
    @patch("api.views.ronda_view.notificar_mesa_actualizada")
    @patch("api.views.ronda_view.get_mano_actual")
    @patch("api.views.ronda_view.ronda_service.jugar_carta")
    def test_jugar_carta_notifies_when_mano_finishes(self, service_mock, mano_mock, _notify_mesa_mock, notify_mano_mock):
        service_mock.return_value = True
        mano_mock.return_value = self.mano
        url = reverse("jugar-carta", args=[self.partida.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.put(url, {"carta": "CARTA_A"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notify_mano_mock.assert_called_once_with(self.partida.id, self.mano.id)
