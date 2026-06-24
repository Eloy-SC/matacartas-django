from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.models.rango import Rango


class PartidaAPITest(APITestCase):
	def setUp(self):
		UserModel = get_user_model()
		self.creador = UserModel.objects.create_user(
			username="creador",
			password="creador-pass-123",
			email="creador@example.com",
			nombre="Creador",
		)
		self.jugador = UserModel.objects.create_user(
			username="jugador",
			password="jugador-pass-123",
			email="jugador@example.com",
			nombre="Jugador",
		)
		self.otro = UserModel.objects.create_user(
			username="otro",
			password="otro-pass-123",
			email="otro@example.com",
			nombre="Otro",
		)

		self.rango_min = Rango.objects.create(
			nombre="NovatoPartida",
			color=Rango.Color.AZUL_CLARO,
			puntos_minimos=1000,
			puntos_maximos=1099,
		)
		self.rango_max = Rango.objects.create(
			nombre="VeteranoPartida",
			color=Rango.Color.AZUL,
			puntos_minimos=1100,
			puntos_maximos=1199,
		)

		self.partida_publica = Partida.objects.create(
			nombre="PartidaPublicaTest",
			num_jugadores=2,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.NORMAL,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=90,
		)
		self.partida_privada = Partida.objects.create(
			nombre="PartidaPrivadaTest",
			num_jugadores=2,
			privada=True,
			clave="abc123",
			longitud=Partida.LongitudPartida.CORTA,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=60,
			rango_minimo=self.rango_min,
			rango_maximo=self.rango_max,
		)

		PartidaUsuario.objects.create(
			partida=self.partida_publica,
			usuario=self.creador,
			creador=True,
			listo=False,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_privada,
			usuario=self.creador,
			creador=True,
			listo=False,
		)

	def _payload_partida(self, **overrides):
		payload = {
			"nombre": "PartidaNuevaApi",
			"num_jugadores": 2,
			"privada": False,
			"clave": None,
			"longitud": Partida.LongitudPartida.NORMAL,
			"cartas_especiales": True,
			"tickets": True,
			"tiempo_max_turno": 90,
			"rango_minimo_id": None,
			"rango_maximo_id": None,
		}
		payload.update(overrides)
		return payload

	def test_listar_partidas_publicas_requires_active_user(self):
		url = reverse("listar-partidas-publicas")
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_listar_partidas_publicas_returns_items(self):
		url = reverse("listar-partidas-publicas")
		self.client.force_authenticate(user=self.creador)

		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(response.data["total"], 1)
		self.assertGreaterEqual(len(response.data["items"]), 1)

	def test_crear_partida_requires_active_user(self):
		url = reverse("crear-partida")
		payload = self._payload_partida()

		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_crear_partida_creates_partida(self):
		url = reverse("crear-partida")
		payload = self._payload_partida(nombre="PartidaCreadaApi")
		self.client.force_authenticate(user=self.jugador)

		response = self.client.post(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Partida.objects.filter(nombre="PartidaCreadaApi").exists())

	def test_editar_partida_updates_partida(self):
		url = reverse("editar-partida", args=[self.partida_publica.id])
		payload = self._payload_partida(
			nombre="PartidaPublicaEditada",
			num_jugadores=3,
		)
		self.client.force_authenticate(user=self.creador)

		with patch("api.views.partida_view.notificar_sala_actualizada"):
			response = self.client.put(url, payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.partida_publica.refresh_from_db()
		self.assertEqual(self.partida_publica.nombre, "PartidaPublicaEditada")
		self.assertEqual(self.partida_publica.num_jugadores, 3)

	def test_get_partida_como_jugador_returns_item(self):
		url = reverse("get-partida-como-jugador", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.creador)

		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["nombre"], "PartidaPublicaTest")

	def test_get_partida_como_jugador_returns_403_for_non_member(self):
		url = reverse("get-partida-como-jugador", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.otro)

		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_get_jugadores_partida_returns_players(self):
		url = reverse("get-jugadores-partida", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.creador)

		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response.data), 1)
		self.assertEqual(response.data[0]["nombre"], "Creador")

	def test_get_jugador_participa_en_partida_returns_true(self):
		url = reverse("get-jugador-participa-en-partida", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.creador)

		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data["participa"])

	def test_get_jugador_participa_en_partida_privada_returns_false(self):
		url = reverse(
			"get-jugador-participa-en-partida-privada",
			args=[self.partida_privada.clave],
		)
		self.client.force_authenticate(user=self.jugador)

		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(response.data["participa"])

	@patch("api.views.partida_view.notificar_sala_actualizada")
	def test_unirse_a_partida_publica_adds_player(self, _notify_mock):
		url = reverse("unirse-a-partida-publica", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.jugador)

		response = self.client.post(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(
			PartidaUsuario.objects.filter(
				partida=self.partida_publica,
				usuario=self.jugador,
			).exists()
		)

	@patch("api.views.partida_view.notificar_sala_actualizada")
	def test_unirse_a_partida_privada_adds_player(self, _notify_mock):
		url = reverse("unirse-a-partida-privada", args=[self.partida_privada.clave])
		self.client.force_authenticate(user=self.jugador)

		response = self.client.post(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(
			PartidaUsuario.objects.filter(
				partida=self.partida_privada,
				usuario=self.jugador,
			).exists()
		)

	@patch("api.views.partida_view.notificar_sala_actualizada")
	def test_toggle_listo_changes_ready_state(self, _notify_mock):
		url = reverse("toggle-listo", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.creador)

		response = self.client.put(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		partida_usuario = PartidaUsuario.objects.get(
			partida=self.partida_publica,
			usuario=self.creador,
		)
		self.assertTrue(partida_usuario.listo)

	@patch("api.views.partida_view.notificar_sala_actualizada")
	def test_abandonar_partida_removes_player(self, _notify_mock):
		PartidaUsuario.objects.create(
			partida=self.partida_publica,
			usuario=self.jugador,
			creador=False,
		)
		url = reverse("abandonar-partida", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.jugador)

		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(
			PartidaUsuario.objects.filter(
				partida=self.partida_publica,
				usuario=self.jugador,
			).exists()
		)

	@patch("api.views.partida_view.notificar_sala_actualizada")
	def test_expulsar_jugador_kicks_player(self, _notify_mock):
		PartidaUsuario.objects.create(
			partida=self.partida_publica,
			usuario=self.jugador,
			creador=False,
		)
		url = reverse(
			"expulsar-jugador",
			args=[self.partida_publica.id, self.jugador.id],
		)
		self.client.force_authenticate(user=self.creador)

		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(
			PartidaUsuario.objects.filter(
				partida=self.partida_publica,
				usuario=self.jugador,
			).exists()
		)

	@patch("api.views.partida_view.notificar_inicio_partida")
	def test_iniciar_partida_starts_match(self, _notify_mock):
		self.partida_publica.num_jugadores = 2
		self.partida_publica.save()

		PartidaUsuario.objects.create(
			partida=self.partida_publica,
			usuario=self.jugador,
			creador=False,
			listo=True,
		)
		pu_creador = PartidaUsuario.objects.get(
			partida=self.partida_publica,
			usuario=self.creador,
		)
		pu_creador.listo = True
		pu_creador.save()

		url = reverse("iniciar-partida", args=[self.partida_publica.id])
		self.client.force_authenticate(user=self.creador)

		response = self.client.put(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.partida_publica.refresh_from_db()
		self.assertIsNotNone(self.partida_publica.fecha_inicio)
