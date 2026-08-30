from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.configuracion_global import ConfiguracionGlobal
from api.models.rango import Rango
from api.models.torneo import Torneo


class TorneoAPITest(APITestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.creator = UserModel.objects.create_user(
            username="torneo-api-creator",
            password="creator-pass-123",
            email="torneo-api-creator@example.com",
            nombre="Torneo API Creator",
        )
        self.creator.puntuacion = 1600
        self.creator.save(update_fields=["puntuacion"])

        self.low_score_user = UserModel.objects.create_user(
            username="torneo-api-low",
            password="low-pass-123",
            email="torneo-api-low@example.com",
            nombre="Torneo API Low",
        )
        self.low_score_user.puntuacion = 900
        self.low_score_user.save(update_fields=["puntuacion"])

        self.rango_min = Rango.objects.create(
            nombre="RangoMinTorneoApi",
            color=Rango.Color.VERDE_CLARO,
            puntos_minimos=1000,
            puntos_maximos=1499,
        )
        self.rango_max = Rango.objects.create(
            nombre="RangoMaxTorneoApi",
            color=Rango.Color.VERDE,
            puntos_minimos=1500,
            puntos_maximos=1999,
        )

        Torneo.objects.create(
            nombre="TorneoApiExistente",
            rango_minimo=self.rango_min,
            rango_maximo=self.rango_max,
            num_jug_fin=4,
            num_jug_sem=4,
            num_jug_cua=4,
            num_jug_oct=None,
            partidas_longitud=Torneo.LongitudPartidaDeTorneo.NORMAL,
            partidas_cartas_especiales=True,
            partidas_tickets=True,
            partidas_tiempo_max_turno=90,
            desempate_mayor_punt=True,
        )

        self.config, _ = ConfiguracionGlobal.objects.get_or_create(id=1)
        self.config.rango_minimo_crear_torneo = self.rango_min
        self.config.save(update_fields=["rango_minimo_crear_torneo"])

    def _payload_torneo(self, **overrides):
        payload = {
            "nombre": "TorneoNuevoApi",
            "rango_minimo_id": self.rango_min.id,
            "rango_maximo_id": self.rango_max.id,
            "num_jug_fin": 4,
            "num_jug_sem": 4,
            "num_jug_cua": 4,
            "num_jug_oct": None,
            "partidas_longitud": Torneo.LongitudPartidaDeTorneo.NORMAL,
            "partidas_cartas_especiales": True,
            "partidas_tickets": True,
            "partidas_tiempo_max_turno": 90,
            "desempate_mayor_punt": True,
        }
        payload.update(overrides)
        return payload

    def test_listar_torneos_publicos_requires_active_user(self):
        url = reverse("listar-torneos-publicos")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_listar_torneos_publicos_returns_items(self):
        url = reverse("listar-torneos-publicos")
        self.client.force_authenticate(user=self.creator)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total"], 1)
        self.assertGreaterEqual(len(response.data["items"]), 1)

    def test_crear_torneo_requires_active_user(self):
        url = reverse("crear-torneo")
        payload = self._payload_torneo()

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_torneo_creates_torneo(self):
        url = reverse("crear-torneo")
        payload = self._payload_torneo(nombre="TorneoCreadoApi")
        self.client.force_authenticate(user=self.creator)

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Torneo.objects.filter(nombre="TorneoCreadoApi").exists())

    def test_crear_torneo_rejects_user_below_required_rank(self):
        url = reverse("crear-torneo")
        payload = self._payload_torneo(nombre="TorneoNoPermitidoApi")
        self.client.force_authenticate(user=self.low_score_user)

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_torneo_returns_item(self):
        url = reverse("get-torneo", args=[self.creator.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_torneo_returns_404_when_missing(self):
        url = reverse("get-torneo", args=[9999])
        self.client.force_authenticate(user=self.creator)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_participantes_torneo_returns_items(self):
        torneo = Torneo.objects.create(
            nombre="TorneoParticipantesApi",
            rango_minimo=self.rango_min,
            rango_maximo=self.rango_max,
            num_jug_fin=4,
            num_jug_sem=4,
            num_jug_cua=4,
            num_jug_oct=None,
            partidas_longitud=Torneo.LongitudPartidaDeTorneo.NORMAL,
            partidas_cartas_especiales=True,
            partidas_tickets=True,
            partidas_tiempo_max_turno=90,
            desempate_mayor_punt=True,
        )
        url = reverse("get-participantes-torneo", args=[torneo.id])
        self.client.force_authenticate(user=self.creator)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_unirse_a_torneo_creates_relation(self):
        user = get_user_model().objects.create_user(
            username="torneo-join-api",
            password="join-pass-123",
            email="torneo-join-api@example.com",
            nombre="Join API",
        )
        user.puntuacion = 1600
        user.save(update_fields=["puntuacion"])

        url = reverse("unirse-a-torneo", args=[self.creator.id])
        self.client.force_authenticate(user=user)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
