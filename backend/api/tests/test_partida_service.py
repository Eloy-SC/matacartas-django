from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.models.rango import Rango
from api.services import partida_service
from api.utils.exceptions import RegistrationError


class PartidaServiceTests(TestCase):
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
		self.started_player = UserModel.objects.create_user(
			username="started-player",
			password="player-pass-123",
			email="started-player@example.com",
			nombre="Started Player",
		)
		self.outsider = UserModel.objects.create_user(
			username="outsider",
			password="outsider-pass-123",
			email="outsider@example.com",
			nombre="Outsider",
		)

		self.creator.puntuacion = 1500
		self.creator.save()
		self.player.puntuacion = 1600
		self.player.save()
		self.started_player.puntuacion = 1550
		self.started_player.save()
		self.outsider.puntuacion = 1700
		self.outsider.save()

		self.rango_min = Rango.objects.create(
			nombre="RangoMinPartidaService",
			color=Rango.Color.VERDE_CLARO,
			puntos_minimos=1000,
			puntos_maximos=1999,
		)
		self.rango_max = Rango.objects.create(
			nombre="RangoMaxPartidaService",
			color=Rango.Color.VERDE,
			puntos_minimos=2000,
			puntos_maximos=2999,
		)

		self.partida_publica = Partida.objects.create(
			nombre="PartidaServicePublica",
			num_jugadores=3,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.NORMAL,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=90,
			rango_minimo=self.rango_min,
			rango_maximo=self.rango_max,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_publica,
			usuario=self.creator,
			creador=True,
			listo=True,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_publica,
			usuario=self.player,
			creador=False,
			listo=False,
		)

		self.partida_privada = Partida.objects.create(
			nombre="PartidaServicePrivada",
			num_jugadores=2,
			privada=True,
			clave="clavepartidaservice",
			longitud=Partida.LongitudPartida.CORTA,
			cartas_especiales=False,
			tickets=False,
			tiempo_max_turno=60,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_privada,
			usuario=self.creator,
			creador=True,
			listo=False,
		)

		self.partida_iniciada = Partida.objects.create(
			nombre="PartidaServiceIniciada",
			num_jugadores=2,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.CORTA,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=60,
			fecha_inicio=timezone.now(),
		)
		PartidaUsuario.objects.create(
			partida=self.partida_iniciada,
			usuario=self.creator,
			creador=True,
			listo=True,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_iniciada,
			usuario=self.started_player,
			creador=False,
			listo=True,
		)

		self.partida_no_listos = Partida.objects.create(
			nombre="PartidaServiceNoListos",
			num_jugadores=2,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.NORMAL,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=90,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_no_listos,
			usuario=self.creator,
			creador=True,
			listo=True,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_no_listos,
			usuario=self.player,
			creador=False,
			listo=False,
		)

		self.partida_lista = Partida.objects.create(
			nombre="PartidaServiceLista",
			num_jugadores=2,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.LARGA,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=120,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_lista,
			usuario=self.creator,
			creador=True,
			listo=True,
		)
		PartidaUsuario.objects.create(
			partida=self.partida_lista,
			usuario=self.started_player,
			creador=False,
			listo=True,
		)

	def test_listar_partidas_publicas_requires_authenticated_user(self):
		with self.assertRaises(PermissionError):
			partida_service.listar_partidas_publicas(
				AnonymousUser(),
				page=1,
				page_size=10,
			)

	def test_listar_partidas_publicas_returns_paged_values(self):
		paged = partida_service.listar_partidas_publicas(
			self.creator,
			page=1,
			page_size=10,
		)
		self.assertEqual(paged["page"], 1)
		self.assertEqual(paged["page_size"], 10)
		self.assertGreaterEqual(paged["total"], 1)
		self.assertIn("items", paged)
		self.assertGreaterEqual(len(paged["items"]), 1)
		self.assertIn("nombre", paged["items"][0])

	def test_crear_partida_requires_authenticated_user(self):
		with self.assertRaises(PermissionError):
			partida_service.crear_partida(
				AnonymousUser(),
				nombre="PartidaServiceNuevaAuth",
				num_jugadores=2,
				privada=False,
				clave=None,
				longitud=Partida.LongitudPartida.NORMAL,
				cartas_especiales=True,
				tickets=True,
				tiempo_max_turno=90,
				rango_minimo_id=None,
				rango_maximo_id=None,
			)

	def test_crear_partida_rejects_duplicate_name(self):
		with self.assertRaises(RegistrationError):
			partida_service.crear_partida(
				self.outsider,
				nombre=self.partida_publica.nombre,
				num_jugadores=2,
				privada=False,
				clave=None,
				longitud=Partida.LongitudPartida.NORMAL,
				cartas_especiales=True,
				tickets=True,
				tiempo_max_turno=90,
				rango_minimo_id=None,
				rango_maximo_id=None,
			)

	def test_crear_partida_creates_partida_and_creator_relation(self):
		partida = partida_service.crear_partida(
			self.outsider,
			nombre="PartidaServiceNueva",
			num_jugadores=2,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.NORMAL,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=90,
			rango_minimo_id=None,
			rango_maximo_id=None,
		)

		self.assertEqual(partida.nombre, "PartidaServiceNueva")
		self.assertTrue(
			PartidaUsuario.objects.filter(
				partida=partida,
				usuario=self.outsider,
				creador=True,
			).exists()
		)

	def test_editar_partida_requires_creator(self):
		with self.assertRaises(PermissionError):
			partida_service.editar_partida(
				self.player,
				self.partida_publica.id,
				nombre="PartidaServicePublicaEditada",
				num_jugadores=4,
				privada=False,
				clave=None,
				longitud=Partida.LongitudPartida.NORMAL,
				cartas_especiales=False,
				tickets=False,
				tiempo_max_turno=100,
				rango_minimo_id=self.rango_min.id,
				rango_maximo_id=self.rango_max.id,
			)

	def test_editar_partida_raises_when_missing(self):
		with self.assertRaises(ValueError):
			partida_service.editar_partida(
				self.creator,
				9999,
				nombre="PartidaServicePublicaEditada",
				num_jugadores=4,
				privada=False,
				clave=None,
				longitud=Partida.LongitudPartida.NORMAL,
				cartas_especiales=False,
				tickets=False,
				tiempo_max_turno=100,
				rango_minimo_id=self.rango_min.id,
				rango_maximo_id=self.rango_max.id,
			)

	def test_editar_partida_updates_partida(self):
		updated = partida_service.editar_partida(
			self.creator,
			self.partida_publica.id,
			nombre="PartidaServicePublicaEditada",
			num_jugadores=4,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.LARGA,
			cartas_especiales=False,
			tickets=False,
			tiempo_max_turno=120,
			rango_minimo_id=self.rango_min.id,
			rango_maximo_id=self.rango_max.id,
		)
		self.assertEqual(updated.nombre, "PartidaServicePublicaEditada")
		self.assertEqual(updated.num_jugadores, 4)
		self.assertEqual(updated.longitud, Partida.LongitudPartida.LARGA)

	def test_get_partida_como_jugador_requires_membership(self):
		with self.assertRaises(PermissionError):
			partida_service.get_partida_como_jugador(self.outsider, self.partida_publica.id)

	def test_get_partida_como_jugador_returns_partida(self):
		partida = partida_service.get_partida_como_jugador(self.player, self.partida_publica.id)
		self.assertEqual(partida.id, self.partida_publica.id)

	def test_get_jugadores_partida_requires_authenticated_user(self):
		with self.assertRaises(PermissionError):
			partida_service.get_jugadores_partida(AnonymousUser(), self.partida_publica.id)

	def test_get_jugadores_partida_returns_players(self):
		jugadores = partida_service.get_jugadores_partida(self.creator, self.partida_publica.id)
		self.assertGreaterEqual(len(jugadores), 2)
		self.assertIn("nombre", jugadores[0])

	def test_get_partida_jugador_raises_when_missing(self):
		with self.assertRaises(ValueError):
			partida_service.get_partida_jugador(self.outsider, self.partida_publica.id)

	def test_get_partida_jugador_returns_relation(self):
		partida_usuario = partida_service.get_partida_jugador(self.creator, self.partida_publica.id)
		self.assertTrue(partida_usuario.creador)

	def test_abandonar_partida_raises_when_not_member(self):
		with self.assertRaises(ValueError):
			partida_service.abandonar_partida(self.outsider, self.partida_publica.id)

	def test_abandonar_partida_reassigns_creator_when_current_leaves(self):
		partida_service.abandonar_partida(self.creator, self.partida_publica.id)

		self.assertFalse(
			PartidaUsuario.objects.filter(
				partida=self.partida_publica,
				usuario=self.creator,
			).exists()
		)
		self.assertTrue(
			PartidaUsuario.objects.filter(
				partida=self.partida_publica,
				usuario=self.player,
				creador=True,
			).exists()
		)

	def test_abandonar_partida_deletes_partida_when_last_player_leaves(self):
		partida_solo = Partida.objects.create(
			nombre="PartidaServiceSolo",
			num_jugadores=2,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.NORMAL,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=90,
		)
		PartidaUsuario.objects.create(
			partida=partida_solo,
			usuario=self.outsider,
			creador=True,
			listo=False,
		)

		partida_service.abandonar_partida(self.outsider, partida_solo.id)
		self.assertFalse(Partida.objects.filter(id=partida_solo.id).exists())

	def test_unirse_a_partida_publica_requires_authenticated_user(self):
		with self.assertRaises(PermissionError):
			partida_service.unirse_a_partida_publica(AnonymousUser(), self.partida_publica.id)

	def test_unirse_a_partida_publica_raises_when_full(self):
		partida_llena = Partida.objects.create(
			nombre="PartidaServiceLlena",
			num_jugadores=2,
			privada=False,
			clave=None,
			longitud=Partida.LongitudPartida.NORMAL,
			cartas_especiales=True,
			tickets=True,
			tiempo_max_turno=90,
		)
		PartidaUsuario.objects.create(
			partida=partida_llena,
			usuario=self.creator,
			creador=True,
			listo=False,
		)
		PartidaUsuario.objects.create(
			partida=partida_llena,
			usuario=self.player,
			creador=False,
			listo=False,
		)

		with self.assertRaises(ValueError):
			partida_service.unirse_a_partida_publica(self.outsider, partida_llena.id)

	def test_unirse_a_partida_publica_joins_partida(self):
		partida_service.unirse_a_partida_publica(self.outsider, self.partida_publica.id)
		self.assertTrue(
			PartidaUsuario.objects.filter(
				partida=self.partida_publica,
				usuario=self.outsider,
			).exists()
		)

	def test_unirse_a_partida_privada_requires_authenticated_user(self):
		with self.assertRaises(PermissionError):
			partida_service.unirse_a_partida_privada(AnonymousUser(), self.partida_privada.clave)

	def test_unirse_a_partida_privada_raises_when_missing(self):
		with self.assertRaises(ValueError):
			partida_service.unirse_a_partida_privada(self.outsider, "clave-inexistente")

	def test_unirse_a_partida_privada_joins_partida(self):
		partida_service.unirse_a_partida_privada(self.outsider, self.partida_privada.clave)
		self.assertTrue(
			PartidaUsuario.objects.filter(
				partida=self.partida_privada,
				usuario=self.outsider,
			).exists()
		)

	def test_toggle_listo_raises_when_not_member(self):
		with self.assertRaises(ValueError):
			partida_service.toggle_listo(self.outsider, self.partida_publica.id)

	def test_toggle_listo_switches_state(self):
		partida_usuario = PartidaUsuario.objects.get(
			partida=self.partida_publica,
			usuario=self.player,
		)
		self.assertFalse(partida_usuario.listo)

		partida_service.toggle_listo(self.player, self.partida_publica.id)

		partida_usuario.refresh_from_db()
		self.assertTrue(partida_usuario.listo)

	def test_expulsar_jugador_requires_creator(self):
		with self.assertRaises(PermissionError):
			partida_service.expulsar_jugador(self.player, self.partida_publica.id, self.creator.id)

	def test_expulsar_jugador_raises_when_missing_target(self):
		with self.assertRaises(ValueError):
			partida_service.expulsar_jugador(self.creator, self.partida_publica.id, 9999)

	def test_expulsar_jugador_raises_when_partida_started(self):
		with self.assertRaises(ValueError):
			partida_service.expulsar_jugador(
				self.creator,
				self.partida_iniciada.id,
				self.started_player.id,
			)

	def test_expulsar_jugador_removes_player(self):
		partida_service.expulsar_jugador(self.creator, self.partida_publica.id, self.player.id)
		self.assertFalse(
			PartidaUsuario.objects.filter(
				partida=self.partida_publica,
				usuario=self.player,
			).exists()
		)

	def test_iniciar_partida_requires_creator(self):
		with self.assertRaises(PermissionError):
			partida_service.iniciar_partida(self.player, self.partida_no_listos.id)

	def test_iniciar_partida_raises_when_not_all_ready(self):
		with self.assertRaises(ValueError):
			partida_service.iniciar_partida(self.creator, self.partida_no_listos.id)

	def test_iniciar_partida_sets_start_date(self):
		partida_service.iniciar_partida(self.creator, self.partida_lista.id)
		self.partida_lista.refresh_from_db()
		self.assertIsNotNone(self.partida_lista.fecha_inicio)
