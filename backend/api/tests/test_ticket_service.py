from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.services import ticket_service
from api.models.catalogo_cartas import CATALOGO
from api.models.mano import Mano
from api.models.ronda import Ronda
from api.services.resumen_mano_service import create_resumen_mano
from api.models.resumen_mano import ResumenMano


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
            cartas=[],
            carta_comodin=None,
        )
        self.pu_player = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.player,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.AZUL,
            puntos=7,
            ticket=None,
            cartas=[],
            carta_comodin=None,
        )
        self.pu_player2 = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.player2,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.VERDE,
            puntos=9,
            ticket=None,
            cartas=[],
            carta_comodin=None,
        )

    def set_up_ronda_cambios(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.ROJO
        self.partida.save(update_fields=["turno_actual"])
        self.mano = Mano.objects.create(partida=self.partida, num=1)
        self.resumen_mano = ResumenMano.objects.create(
            mano=self.mano,
            tickets_usados={"0":[], "1":[], "2":[], "3":[]},
            victorias={},
            muertes={},
            retiradas={"1":[], "2":[], "3":[]},
            efectos_inmediatos_ronda={"1":[], "2":[], "3":[]},
            efectos_extra_fin_mano=[]
        )
        self.ronda = Ronda.objects.create(mano=self.mano, num=0, cartas={}, cambios=0)

    def set_up_ronda_lances(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.ROJO
        self.partida.save(update_fields=["turno_actual"])
        self.mano = Mano.objects.create(partida=self.partida, num=1)
        self.resumen_mano = ResumenMano.objects.create(
            mano=self.mano,
            tickets_usados={"0":[], "1":[], "2":[], "3":[]},
            victorias={},
            muertes={},
            retiradas={"1":[], "2":[], "3":[]},
            efectos_inmediatos_ronda={"1":[], "2":[], "3":[]},
            efectos_extra_fin_mano=[]
        )
        self.ronda = Ronda.objects.create(mano=self.mano, num=1, cartas={}, cambios=2)

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
        self.set_up_ronda_cambios()

        self.pu_creator.ticket = "ticket_cb_aleatorio"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_aleatorio")

        self.partida.refresh_from_db()

        jugadores = PartidaUsuario.objects.filter(
            partida=self.partida
        )

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
        for jugador in jugadores:
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
            [(3, 1), (2, 2), (4, 0),]
        )
        
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertNotEqual(self.partida.baraja, baraja_original)
        self.assertIsNone(self.pu_creator.ticket)

        self.assertEqual(self.partida.turno_actual, self.partida.disposicion_jugadores[0])

    def test_usar_ticket_cb_con_unicas_cambia_baraja_y_elimina_ticket(self):
        self.set_up_ronda_cambios()
        
        self.pu_creator.ticket = "ticket_cb_con_unicas"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_con_unicas")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

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

        self.assertEqual(self.partida.turno_actual, self.partida.disposicion_jugadores[0])

    def test_usar_ticket_cb_valiosa_cambia_baraja_y_elimina_ticket(self):
        self.set_up_ronda_cambios()

        self.pu_creator.ticket = "ticket_cb_valiosa"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_valiosa")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

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

        self.assertEqual(self.partida.turno_actual, self.partida.disposicion_jugadores[0])

    def test_usar_ticket_cb_magica_cambia_baraja_y_elimina_ticket(self):
        self.set_up_ronda_cambios()
        
        self.pu_creator.ticket = "ticket_cb_magica"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_magica")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

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

        self.assertEqual(self.partida.turno_actual, self.partida.disposicion_jugadores[0])

    def test_usar_ticket_cb_unica_cambia_baraja_y_elimina_ticket(self):
        self.set_up_ronda_cambios()

        self.pu_creator.ticket = "ticket_cb_unica"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_unica")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

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

        self.assertEqual(self.partida.turno_actual, self.partida.disposicion_jugadores[0])

    def test_usar_ticket_cb_todas_cambia_baraja_y_elimina_ticket(self):
        self.set_up_ronda_cambios()

        self.pu_creator.ticket = "ticket_cb_todas"
        self.pu_creator.save(update_fields=["ticket"])
        baraja_original = self.partida.baraja.copy()
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cb_todas")

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

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

        self.assertEqual(self.partida.turno_actual, self.partida.disposicion_jugadores[0])

    ## INTERCAMBIO COMODINES
    def test_usar_ticket_ic_azar_intercambia_comodines(self):
        self.set_up_ronda_lances()
        
        self.pu_creator.ticket = "ticket_ic_azar"
        self.pu_creator.carta_comodin = "COMODIN_A"
        self.pu_creator.save(update_fields=["ticket", "carta_comodin"])
        self.pu_player.carta_comodin = "COMODIN_B"
        self.pu_player.save(update_fields=["carta_comodin"])
        self.pu_player2.carta_comodin = "COMODIN_C"
        self.pu_player2.save(update_fields=["carta_comodin"])

        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_ic_azar")

        pu_creator = PartidaUsuario.objects.get(
            partida=self.partida,
            usuario=self.creator,
        )
        pu_player = PartidaUsuario.objects.get(
            partida=self.partida,
            usuario=self.player,
        )
        pu_player2 = PartidaUsuario.objects.get(
            partida=self.partida,
            usuario=self.player2,
        )

        self.assertIn(pu_creator.carta_comodin, ["COMODIN_B", "COMODIN_C"])
        self.assertIn(pu_player.carta_comodin, ["COMODIN_A", "COMODIN_B"])
        self.assertIn(pu_player2.carta_comodin, ["COMODIN_A", "COMODIN_C"])
        self.assertIsNone(pu_creator.ticket)

    def test_usar_ticket_ic_primero_intercambia_comodines(self):
        self.set_up_ronda_lances()
        
        self.pu_creator.ticket = "ticket_ic_primero"
        self.pu_creator.carta_comodin = "COMODIN_A"
        self.pu_creator.save(update_fields=["ticket", "carta_comodin"])
        self.pu_player.carta_comodin = "COMODIN_B"
        self.pu_player.puntos = 10
        self.pu_player.save(update_fields=["carta_comodin", "puntos"])
        self.pu_player2.carta_comodin = "COMODIN_C"
        self.pu_player2.puntos = 6
        self.pu_player2.save(update_fields=["carta_comodin", "puntos"])

        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_ic_primero")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.carta_comodin, "COMODIN_B")
        self.assertEqual(self.pu_player.carta_comodin, "COMODIN_A")
        self.assertEqual(self.pu_player2.carta_comodin, "COMODIN_C")
        self.assertIsNone(self.pu_creator.ticket)

    ## PERDIDA DE PUNTOS
    def test_usar_ticket_pp_todos_2_resta_a_todos(self):
        self.set_up_ronda_lances()
        
        self.pu_creator.ticket = "ticket_pp_2_todos"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_2_todos")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertEqual(self.pu_player.puntos, 5)
        self.assertEqual(self.pu_player2.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_todos_4_resta_a_todos(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_pp_4_todos"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_4_todos")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertEqual(self.pu_player.puntos, 3)
        self.assertEqual(self.pu_player2.puntos, 5)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_todos_6_resta_a_todos(self):
        self.set_up_ronda_lances()
        
        self.pu_creator.ticket = "ticket_pp_6_todos"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_6_todos")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertEqual(self.pu_player.puntos, 1)
        self.assertEqual(self.pu_player2.puntos, 3)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_azar_2_resta_a_jugador_al_azar(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_pp_2_azar"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_2_azar")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertIn(self.pu_player.puntos, [7, 5])
        self.assertIn(self.pu_player2.puntos, [9, 7])
        if self.pu_player.puntos == 5:
            self.assertEqual(self.pu_player2.puntos, 9)
        else:
            self.assertEqual(self.pu_player2.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_azar_4_resta_a_jugador_al_azar(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_pp_4_azar"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_4_azar")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertIn(self.pu_player.puntos, [7, 3])
        self.assertIn(self.pu_player2.puntos, [9, 5])
        if self.pu_player.puntos == 3:
            self.assertEqual(self.pu_player2.puntos, 9)
        else:
            self.assertEqual(self.pu_player2.puntos, 5)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_azar_6_resta_a_jugador_al_azar(self):
        self.set_up_ronda_lances()
                
        self.pu_creator.ticket = "ticket_pp_6_azar"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_6_azar")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertIn(self.pu_player.puntos, [7, 1])
        self.assertIn(self.pu_player2.puntos, [9, 3])
        if self.pu_player.puntos == 1:
            self.assertEqual(self.pu_player2.puntos, 9)
        else:
            self.assertEqual(self.pu_player2.puntos, 3)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_primero_2_resta_a_jugador_primero(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_pp_2_primero"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_2_primero")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertEqual(self.pu_player.puntos, 7)
        self.assertEqual(self.pu_player2.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_primero_4_resta_a_jugador_primero(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_pp_4_primero"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_4_primero")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertEqual(self.pu_player.puntos, 7)
        self.assertEqual(self.pu_player2.puntos, 5)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_pp_primero_6_resta_a_jugador_primero(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_pp_6_primero"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_pp_6_primero")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 5)
        self.assertEqual(self.pu_player.puntos, 7)
        self.assertEqual(self.pu_player2.puntos, 3)
        self.assertIsNone(self.pu_creator.ticket)

    ## ROBO DE PUNTOS
    def test_usar_ticket_rp_2_azar_roba_puntos_y_elimina_ticket(self):
        self.set_up_ronda_lances()
        
        self.pu_creator.ticket = "ticket_rp_2_azar"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_rp_2_azar")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 7)
        self.assertIn(self.pu_player.puntos, [5, 7])
        self.assertIn(self.pu_player2.puntos, [7, 9])
        if self.pu_player.puntos == 5:
            self.assertEqual(self.pu_player2.puntos, 9)
        else:
            self.assertEqual(self.pu_player2.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_rp_2_primero_roba_puntos_y_elimina_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_rp_2_primero"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_rp_2_primero")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 7)
        self.assertEqual(self.pu_player.puntos, 7)
        self.assertEqual(self.pu_player2.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_rp_2_todos_roba_puntos_y_elimina_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_rp_2_todos"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_rp_2_todos")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 9)
        self.assertEqual(self.pu_player.puntos, 5)
        self.assertEqual(self.pu_player2.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    ## RETIRADA OBLIGADA
    def test_usar_ticket_ro_azar_retirada_obligada_y_elimina_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_ro_azar"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_ro_azar")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        if self.pu_player.retirado:
            self.assertEqual(self.pu_player2.retirado, False)
        else:
            self.assertEqual(self.pu_player.retirado, False)
            self.assertEqual(self.pu_player2.retirado, True)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_ro_primero_retirada_obligada_y_elimina_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_ro_primero"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_ro_primero")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_player2.retirado, True)
        self.assertIsNone(self.pu_creator.ticket)

    ## ROBO DE TICKET

    def test_usar_ticket_rt_azar_roba_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_rt_azar"
        self.pu_creator.save(update_fields=["ticket"])
        self.pu_player.ticket = "ticket_cp_2"
        self.pu_player.save(update_fields=["ticket"])
        self.pu_player2.ticket = "ticket_cp_4"
        self.pu_player2.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_rt_azar")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertIn(self.pu_creator.ticket, ["ticket_cp_2", "ticket_cp_4"])
        if self.pu_creator.ticket == "ticket_cp_2":
            self.assertIsNone(self.pu_player.ticket)
            self.assertEqual(self.pu_player2.ticket, "ticket_cp_4")
        else:
            self.assertIsNone(self.pu_player2.ticket)
            self.assertEqual(self.pu_player.ticket, "ticket_cp_2")

    def test_usar_ticket_rt_primero_roba_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_rt_primero"
        self.pu_creator.save(update_fields=["ticket"])
        self.pu_player.ticket = "ticket_cp_2"
        self.pu_player.save(update_fields=["ticket"])
        self.pu_player2.ticket = "ticket_cp_4"
        self.pu_player2.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_rt_primero")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.ticket, "ticket_cp_4")
        self.assertEqual(self.pu_player.ticket, "ticket_cp_2")
        self.assertEqual(self.pu_player2.ticket, None)

    def test_usar_ticket_rt_mayor_clase_roba_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_rt_mayor_clase"
        self.pu_creator.save(update_fields=["ticket"])
        self.pu_player.ticket = "ticket_cp_2"
        self.pu_player.save(update_fields=["ticket"])
        self.pu_player2.ticket = "ticket_cp_4"
        self.pu_player2.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_rt_mayor_clase")

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()

        self.assertEqual(self.pu_creator.ticket, "ticket_cp_4")
        self.assertEqual(self.pu_player.ticket, "ticket_cp_2")
        self.assertEqual(self.pu_player2.ticket, None)

    ## CANJEAR PUNTOS
    def test_usar_ticket_cp_2_suma_puntos_y_elimina_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_cp_2"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_2")

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 7)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cp_4_suma_puntos_y_elimina_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_cp_4"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_4")

        self.pu_creator.refresh_from_db()
        
        self.assertEqual(self.pu_creator.puntos, 9)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cp_6_suma_puntos_y_elimina_ticket(self):
        self.set_up_ronda_lances()

        self.pu_creator.ticket = "ticket_cp_6"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_6")

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 11)
        self.assertIsNone(self.pu_creator.ticket)

    def test_usar_ticket_cp_10_suma_puntos_y_elimina_ticket(self):
        self.set_up_ronda_lances()
        
        self.pu_creator.ticket = "ticket_cp_10"
        self.pu_creator.save(update_fields=["ticket"])
        ticket_service.usar_ticket(self.creator, self.partida.id, "ticket_cp_10")

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 15)
        self.assertIsNone(self.pu_creator.ticket)
