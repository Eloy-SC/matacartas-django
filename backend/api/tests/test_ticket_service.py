from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.services import ticket_service
from api.models.catalogo_cartas import CATALOGO


class TicketServiceTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.creator = UserModel.objects.create_user(
            username="creator_ticket",
            password="creator-pass-123",
            email="creator_ticket@example.com",
            nombre="Creator Ticket",
        )
        self.player = UserModel.objects.create_user(
            username="player_ticket",
            password="player-pass-123",
            email="player_ticket@example.com",
            nombre="Player Ticket",
        )
        self.player2 = UserModel.objects.create_user(
            username="player2_ticket",
            password="player2-pass-123",
            email="player2_ticket@example.com",
            nombre="Player2 Ticket",
        )
        self.outsider = UserModel.objects.create_user(
            username="outsider_ticket",
            password="outsider-pass-123",
            email="outsider_ticket@example.com",
            nombre="Outsider Ticket",
        )

        self.partida = Partida.objects.create(
            nombre="PartidaTicketService",
            num_jugadores=3,
            privada=False,
            clave=None,
            longitud=Partida.LongitudPartida.NORMAL,
            cartas_especiales=True,
            tickets=True,
            tiempo_max_turno=90,
            turno_actual=PartidaUsuario.ColorJugador.ROJO,
            disposicion_jugadores=[
                PartidaUsuario.ColorJugador.ROJO,
                PartidaUsuario.ColorJugador.AZUL,
                PartidaUsuario.ColorJugador.VERDE,
            ],
        )

        self.pu_creator = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.creator,
            creador=True,
            listo=True,
            color=PartidaUsuario.ColorJugador.ROJO,
            puntos=5,
            ticket=None,
        )
        self.pu_player = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.player,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.AZUL,
            puntos=7,
            ticket=None,
        )
        self.pu_player2 = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.player2,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.VERDE,
            puntos=9,
            ticket=None,
        )

    def test_usar_ticket_rechaza_usuario_fuera_de_la_partida(self):
        with self.assertRaises(PermissionError):
            ticket_service.usar_ticket(self.outsider, self.partida.id, "ticket_cp_2")

    def test_usar_ticket_rechaza_ticket_distinto(self):
        self.pu_creator.ticket = "ticket_cp_2"
        self.pu_creator.save(update_fields=["ticket"])
        with self.assertRaises(ValueError):
            ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_6")

    def test_usar_ticket_rechaza_si_no_es_turno_del_jugador(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.AZUL
        self.partida.save(update_fields=["turno_actual"])

        self.pu_creator.ticket = "ticket_cp_2"
        self.pu_creator.save(update_fields=["ticket"])

        with self.assertRaises(PermissionError):
            ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_2")

    ## CAMBIO BARAJA
    def test_usar_ticket_cb_aleatorio_cambia_baraja_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cb_aleatorio"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_aleatorio")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()

        self.assertNotEqual(self.partida.baraja, baraja_original)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cb_con_unicas_cambia_baraja_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cb_con_unicas"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_con_unicas")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()

        contador_valiosas = 0
        contador_magicas = 0
        contador_unicas = 0
        for carta in self.partida.baraja:
            if CATALOGO[carta]["tipo"] == "especial_val":
                contador_valiosas += 1
            elif CATALOGO[carta]["tipo"] == "especial_mag":
                contador_magicas += 1
            elif CATALOGO[carta]["tipo"] == "especial_uni":
                contador_unicas += 1
        for jugador in [self.pu_creator, self.pu_player, self.pu_player2]:
            for carta in jugador.cartas:
                if CATALOGO[carta]["tipo"] == "especial_val":
                    contador_valiosas += 1
                elif CATALOGO[carta]["tipo"] == "especial_mag":
                    contador_magicas += 1
                elif CATALOGO[carta]["tipo"] == "especial_uni":
                    contador_unicas += 1

        self.assertEqual(contador_valiosas, 8)
        self.assertIn(
            (contador_magicas, contador_unicas),
            [(3, 1), (2, 2)]
        )

        self.assertNotEqual(self.partida.baraja, baraja_original)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cb_valiosa_cambia_baraja_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cb_valiosa"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_valiosa")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()

        contador_valiosas = 0
        contador_magicas = 0
        contador_unicas = 0
        for carta in self.partida.baraja:
            if CATALOGO[carta]["tipo"] == "especial_val":
                contador_valiosas += 1
            elif CATALOGO[carta]["tipo"] == "especial_mag":
                contador_magicas += 1
            elif CATALOGO[carta]["tipo"] == "especial_uni":
                contador_unicas += 1
        for jugador in [self.pu_creator, self.pu_player, self.pu_player2]:
            for carta in jugador.cartas:
                if CATALOGO[carta]["tipo"] == "especial_val":
                    contador_valiosas += 1
                elif CATALOGO[carta]["tipo"] == "especial_mag":
                    contador_magicas += 1
                elif CATALOGO[carta]["tipo"] == "especial_uni":
                    contador_unicas += 1

        self.assertEqual(contador_valiosas, 12)
        self.assertEqual(contador_magicas, 0)
        self.assertEqual(contador_unicas, 0)

        self.assertNotEqual(self.partida.baraja, baraja_original)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cb_magica_cambia_baraja_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cb_magica"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_magica")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()

        contador_valiosas = 0
        contador_magicas = 0
        contador_unicas = 0
        for carta in self.partida.baraja:
            if CATALOGO[carta]["tipo"] == "especial_val":
                contador_valiosas += 1
            elif CATALOGO[carta]["tipo"] == "especial_mag":
                contador_magicas += 1
            elif CATALOGO[carta]["tipo"] == "especial_uni":
                contador_unicas += 1
        for jugador in [self.pu_creator, self.pu_player, self.pu_player2]:
            for carta in jugador.cartas:
                if CATALOGO[carta]["tipo"] == "especial_val":
                    contador_valiosas += 1
                elif CATALOGO[carta]["tipo"] == "especial_mag":
                    contador_magicas += 1
                elif CATALOGO[carta]["tipo"] == "especial_uni":
                    contador_unicas += 1

        self.assertEqual(contador_valiosas, 8)
        self.assertEqual(contador_magicas, 6)
        self.assertEqual(contador_unicas, 0)

        self.assertNotEqual(self.partida.baraja, baraja_original)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cb_unica_cambia_baraja_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cb_unica"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_unica")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()

        contador_valiosas = 0
        contador_magicas = 0
        contador_unicas = 0
        for carta in self.partida.baraja:
            if CATALOGO[carta]["tipo"] == "especial_val":
                contador_valiosas += 1
            elif CATALOGO[carta]["tipo"] == "especial_mag":
                contador_magicas += 1
            elif CATALOGO[carta]["tipo"] == "especial_uni":
                contador_unicas += 1
        for jugador in [self.pu_creator, self.pu_player, self.pu_player2]:
            for carta in jugador.cartas:
                if CATALOGO[carta]["tipo"] == "especial_val":
                    contador_valiosas += 1
                elif CATALOGO[carta]["tipo"] == "especial_mag":
                    contador_magicas += 1
                elif CATALOGO[carta]["tipo"] == "especial_uni":
                    contador_unicas += 1

        self.assertEqual(contador_valiosas, 8)
        self.assertEqual(contador_magicas, 4)
        self.assertEqual(contador_unicas, 2)
        self.assertNotEqual(self.partida.baraja, baraja_original)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cb_todas_cambia_baraja_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cb_todas"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_todas")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()

        todas_especiales = True
        for carta in self.partida.baraja:
            if CATALOGO[carta]["tipo"] == "normal":
                todas_especiales = False
                break
        for jugador in [self.pu_creator, self.pu_player, self.pu_player2]:
            for carta in jugador.cartas:
                if CATALOGO[carta]["tipo"] == "normal":
                    todas_especiales = False
                    break
        
        self.assertTrue(todas_especiales)
        self.assertNotEqual(self.partida.baraja, baraja_original)
        self.assertIsNone(self.pu_creator.ticket)

    ## CANJEAR PUNTOS
    def test_usar_ticket_cp_2_suma_puntos_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cp_2"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_2")

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cp_4_suma_puntos_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cp_4"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_4")

        self.pu_creator.refresh_from_db()
        
        self.assertEqual(self.pu_creator.puntos, 9)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cp_6_suma_puntos_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cp_6"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_6")

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 11)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cp_10_suma_puntos_y_elimina_ticket(self):
        self.pu_creator.ticket = "ticket_cp_10"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_10")

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 15)
        self.assertIsNone(self.pu_creator.ticket)



"""
    def test_repartir_tickets_asigna_ticket_al_ultimo_cuando_hay_probabilidad(self):
        self.pu_creator.puntos = 20
        self.pu_creator.save(update_fields=["puntos"])
        self.pu_player.puntos = 10
        self.pu_player.save(update_fields=["puntos"])

        pu_tercero = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.outsider,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.VERDE,
            puntos=0,
            ticket=None,
        )

        with patch("api.services.ticket_service.random.random", return_value=0.0), patch(
            "api.services.ticket_service.random.choices",
            return_value=[3],
        ), patch(
            "api.services.ticket_service.random.choice",
            return_value="ticket_cp_2",
        ):
            ticket_service.repartir_tickets(self.partida.id)

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        pu_tercero.refresh_from_db()

        self.assertIsNone(self.pu_creator.ticket)
        self.assertEqual(self.pu_player.ticket, "ticket_cp_2")
        self.assertEqual(pu_tercero.ticket, "ticket_cp_2")
"""