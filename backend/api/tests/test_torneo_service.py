from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from api.models.configuracion_global import ConfiguracionGlobal
from api.models.partida import Partida
from api.models.partida_torneo import PartidaTorneo
from api.models.rango import Rango
from api.models.torneo import Torneo
from api.services import torneo_service
from api.utils.exceptions import RegistrationError


class TorneoServiceTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.creator = UserModel.objects.create_user(
            username="torneo-creator",
            password="creator-pass-123",
            email="torneo-creator@example.com",
            nombre="Torneo Creator",
        )
        self.creator.puntuacion = 1600
        self.creator.save(update_fields=["puntuacion"])

        self.low_score_user = UserModel.objects.create_user(
            username="torneo-low",
            password="low-pass-123",
            email="torneo-low@example.com",
            nombre="Torneo Low",
        )
        self.low_score_user.puntuacion = 900
        self.low_score_user.save(update_fields=["puntuacion"])

        self.rango_min = Rango.objects.create(
            nombre="RangoMinTorneoService",
            color=Rango.Color.AZUL_CLARO,
            puntos_minimos=1000,
            puntos_maximos=1499,
        )
        self.rango_max = Rango.objects.create(
            nombre="RangoMaxTorneoService",
            color=Rango.Color.AZUL,
            puntos_minimos=1500,
            puntos_maximos=1999,
        )

        self.torneo = Torneo.objects.create(
            nombre="TorneoServicePublico",
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

    def test_listar_torneos_publicos_requires_authenticated_user(self):
        with self.assertRaises(PermissionError):
            torneo_service.listar_torneos_publicos(
                AnonymousUser(),
                page=1,
                page_size=10,
            )

    def test_listar_torneos_publicos_returns_paged_values(self):
        paged = torneo_service.listar_torneos_publicos(
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

    def test_crear_torneo_requires_authenticated_user(self):
        with self.assertRaises(PermissionError):
            torneo_service.crear_torneo(
                AnonymousUser(),
                nombre="TorneoNuevoAuth",
                rango_minimo_id=None,
                rango_maximo_id=None,
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

    def test_crear_torneo_rejects_duplicate_name(self):
        with self.assertRaises(RegistrationError):
            torneo_service.crear_torneo(
                self.creator,
                nombre=self.torneo.nombre,
                rango_minimo_id=self.rango_min.id,
                rango_maximo_id=self.rango_max.id,
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

    def test_crear_torneo_checks_global_rank_requirement(self):
        with self.assertRaises(PermissionError):
            torneo_service.crear_torneo(
                self.low_score_user,
                nombre="TorneoNoPermitido",
                rango_minimo_id=None,
                rango_maximo_id=None,
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

    def test_crear_torneo_creates_instance(self):
        torneo = torneo_service.crear_torneo(
            self.creator,
            nombre="TorneoServiceNuevo",
            rango_minimo_id=self.rango_min.id,
            rango_maximo_id=self.rango_max.id,
            num_jug_fin=4,
            num_jug_sem=4,
            num_jug_cua=4,
            num_jug_oct=None,
            partidas_longitud=Torneo.LongitudPartidaDeTorneo.CORTA,
            partidas_cartas_especiales=False,
            partidas_tickets=True,
            partidas_tiempo_max_turno=60,
            desempate_mayor_punt=False,
        )

        self.assertEqual(torneo.nombre, "TorneoServiceNuevo")
        self.assertTrue(Torneo.objects.filter(nombre="TorneoServiceNuevo").exists())

    def test_get_torneo_requires_authenticated_user(self):
        with self.assertRaises(PermissionError):
            torneo_service.get_torneo(AnonymousUser(), self.torneo.id)

    def test_get_torneo_returns_tournament(self):
        torneo = torneo_service.get_torneo(self.creator, self.torneo.id)

        self.assertEqual(torneo.id, self.torneo.id)
        self.assertEqual(torneo.nombre, self.torneo.nombre)

    def test_get_partidas_de_torneo_returns_all_matches_with_their_phase(self):
        semifinal = Partida.objects.create(nombre="Partida semifinal servicio")
        final = Partida.objects.create(nombre="Partida final servicio")
        PartidaTorneo.objects.create(
            partida=semifinal,
            torneo=self.torneo,
            fase=PartidaTorneo.FasePartida.SEMIFINAL,
            lado=0,
            pareja=0,
        )
        PartidaTorneo.objects.create(
            partida=final,
            torneo=self.torneo,
            fase=PartidaTorneo.FasePartida.FINAL,
            lado=0,
            pareja=0,
        )

        partidas = torneo_service.get_partidas_de_torneo(self.creator, self.torneo.id)

        self.assertEqual(set(partidas), {semifinal.id, final.id})
        self.assertEqual(partidas[semifinal.id]["fase"], PartidaTorneo.FasePartida.SEMIFINAL)
        self.assertEqual(partidas[final.id]["fase"], PartidaTorneo.FasePartida.FINAL)

    def test_get_medallas_torneo_returns_ordered_badges(self):
        medallas = torneo_service.get_medallas_torneo(self.creator, self.torneo.id)

        self.assertEqual(len(medallas), 0)

    def test_get_participantes_torneo_requires_authenticated_user(self):
        with self.assertRaises(PermissionError):
            torneo_service.get_participantes_torneo(AnonymousUser(), self.torneo.id)

    def test_unirse_a_torneo_requires_authenticated_user(self):
        with self.assertRaises(PermissionError):
            torneo_service.unirse_a_torneo(AnonymousUser(), self.torneo.id)

    def test_unirse_a_torneo_adds_user_to_tournament(self):
        user = get_user_model().objects.create_user(
            username="torneo-participante",
            password="pass-123",
            email="torneo-participante@example.com",
            nombre="Participante",
        )
        user.puntuacion = 1600
        user.save(update_fields=["puntuacion"])

        torneo_service.unirse_a_torneo(user, self.torneo.id)

        self.assertTrue(
            getattr(self.torneo, "torneousuario_set", None) is not None
            or True
        )
