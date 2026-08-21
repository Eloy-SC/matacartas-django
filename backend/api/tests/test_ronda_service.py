from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.mano import Mano
from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.models.ronda import Ronda
from api.services import ronda_service
from api.models.resumen_mano import ResumenMano


class RondaServiceTests(TestCase):
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
        self.player2 = UserModel.objects.create_user(
            username="player2",
            password="player2-pass-123",
            email="player2@example.com",
            nombre="Player2",
        )
        self.outsider = UserModel.objects.create_user(
            username="outsider",
            password="outsider-pass-123",
            email="outsider@example.com",
            nombre="Outsider",
        )

        self.partida = Partida.objects.create(
            nombre="PartidaRondaService",
            num_jugadores=3,
            privada=False,
            clave=None,
            longitud=Partida.LongitudPartida.NORMAL,
            cartas_especiales=True,
            tickets=True,
            tiempo_max_turno=90,
            disposicion_jugadores=[
                PartidaUsuario.ColorJugador.ROJO,
                PartidaUsuario.ColorJugador.AZUL,
                PartidaUsuario.ColorJugador.VERDE,
            ],
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
        self.pu_player2 = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.player2,
            creador=False,
            listo=True,
            color=PartidaUsuario.ColorJugador.VERDE,
            cartas=["CARTA_I", "CARTA_J", "CARTA_K", "CARTA_L"],
        )
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

        self.pu_por_color = {
            PartidaUsuario.ColorJugador.ROJO: self.pu_creator,
            PartidaUsuario.ColorJugador.AZUL: self.pu_player,
            PartidaUsuario.ColorJugador.VERDE: self.pu_player2,
        }

    def crear_ronda(self, *, num, cartas, cambios=2, ganador=None):
        return Ronda.objects.create(
            mano=self.mano,
            num=num,
            cartas=cartas,
            cambios=cambios,
            ganador=ganador,
        )

    def jugar_cartas_en_ronda(self, *, num, rojo, azul, verde, cambios=2):
        return self.crear_ronda(
            num=num,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: rojo,
                PartidaUsuario.ColorJugador.AZUL: azul,
                PartidaUsuario.ColorJugador.VERDE: verde,
            },
            cambios=cambios,
        )

    def dar_cartas_a_jugador(self, color, cartas):
        jugador = self.pu_por_color[color]
        jugador.cartas = list(cartas)
        jugador.save(update_fields=["cartas"])

    def test_jugar_carta_updates_round_and_hand(self):
        fin_mano = ronda_service.jugar_carta(self.creator, self.partida.id, "CARTA_A")

        self.assertFalse(fin_mano)
        self.ronda.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.partida.refresh_from_db()

        self.assertEqual(self.ronda.cartas[PartidaUsuario.ColorJugador.ROJO], "CARTA_A")
        self.assertEqual(self.partida.turno_actual, PartidaUsuario.ColorJugador.AZUL)
        self.assertNotIn("CARTA_A", self.pu_creator.cartas)

    def test_jugar_carta_requires_turn(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.AZUL
        self.partida.save(update_fields=["turno_actual"])

        with self.assertRaises(PermissionError):
            ronda_service.jugar_carta(self.creator, self.partida.id, "CARTA_A")

    def test_jugar_carta_rejects_missing_card(self):
        with self.assertRaises(ValueError):
            ronda_service.jugar_carta(self.creator, self.partida.id, "CARTA_X")

# GANADORES DE RONDA

    def test_ganador_ronda_por_carta_alta(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="2_BASTOS",
            azul="3_OROS",
            verde="8_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)

    def test_ganador_ronda_por_muerte(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="7_ESPADAS",
            azul="3_OROS",
            verde="8_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)

    def test_assert_recompensa_puntos_matar_numero(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=2,
            rojo="7_ESPADAS",
            azul="3_OROS",
            verde="8_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_player2.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)
        # Comprobar que el jugador ha recibido 1 punto
        self.assertEqual(self.pu_player2.puntos, 1)

    def test_assert_recompensa_puntos_matar_figura(self):
            ronda_nueva = self.jugar_cartas_en_ronda(
                num=2,
                rojo="10_ESPADAS",
                azul="8_OROS",
                verde="8_COPAS",
            )
    
            ronda_service.ganador_ronda(self.partida.id)

            
            ronda_nueva.refresh_from_db()
            self.pu_player.refresh_from_db()
            self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)
            self.assertEqual(self.pu_player.puntos, 2)

    def test_assert_recompensa_puntos_matar_as(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=2,
            rojo="1_ESPADAS",
            azul="8_OROS",
            verde="7_BASTOS",
        )

        ronda_service.ganador_ronda(self.partida.id)
        
        ronda_nueva.refresh_from_db()
        self.pu_player2.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)
        # Comprobar que el jugador ha recibido 3 puntos
        self.assertEqual(self.pu_player2.puntos, 3)


# PUNTOS EXTRA INMEDIATOS POR RONDA
    def test_assert_recompensa_vinos_viejos(self):
        Ronda.objects.create(
            mano=self.mano,
            num=2,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "4_VINOS_VIEJOS",
                PartidaUsuario.ColorJugador.AZUL: "2_COPAS",
                PartidaUsuario.ColorJugador.VERDE: "7_BASTOS",
            },
            cambios=2,
        )
        self.ronda.save(update_fields=["cartas"])

        ronda_service.ganador_ronda(self.partida.id)
        
        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 2)

    def test_saqueador_roba_puntos_muerte_numero(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="SAQUEADOR_TUMBAS",
            azul="7_ESPADAS",
            verde="8_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)
        self.assertEqual(self.pu_player.acumulador_deaths, 1)
        self.assertEqual(self.pu_player2.acumulador_kills, 1)
        self.assertEqual(self.pu_player2.puntos, 0)
        self.assertEqual(self.pu_creator.puntos, 3)

    def test_saqueador_roba_puntos_muerte_figura(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="SAQUEADOR_TUMBAS",
            azul="10_ESPADAS",
            verde="8_OROS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)
        self.assertEqual(self.pu_player.acumulador_deaths, 1)
        self.assertEqual(self.pu_player2.acumulador_kills, 1)
        self.assertEqual(self.pu_player2.puntos, 0)
        self.assertEqual(self.pu_creator.puntos, 4)

    def test_saqueador_roba_puntos_muerte_as(self):
            ronda_nueva = self.jugar_cartas_en_ronda(
                num=1,
                rojo="SAQUEADOR_TUMBAS",
                azul="1_ESPADAS",
                verde="8_BASTOS",
            )
    
            ronda_service.ganador_ronda(self.partida.id)
    
            ronda_nueva.refresh_from_db()
            self.pu_creator.refresh_from_db()
            self.pu_player.refresh_from_db()
            self.pu_player2.refresh_from_db()
            self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)
            self.assertEqual(self.pu_player.acumulador_deaths, 1)
            self.assertEqual(self.pu_player2.acumulador_kills, 1)
            self.assertEqual(self.pu_player2.puntos, 0)
            self.assertEqual(self.pu_creator.puntos, 5)

    def test_saqueador_no_roba_puntos_si_no_hay_muerte(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="SAQUEADOR_TUMBAS",
            azul="2_ESPADAS",
            verde="3_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)
        self.assertEqual(self.pu_player.acumulador_deaths, 0)
        self.assertEqual(self.pu_player2.acumulador_kills, 0)
        self.assertEqual(self.pu_player2.puntos, 0)
        self.assertEqual(self.pu_creator.puntos, 0)

    def test_saqueador_roba_puntos_muerte_bastos_pun(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="SAQUEADOR_TUMBAS",
            azul="1_COPAS",
            verde="7_BASTOS_PUNTIAGUDOS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_player2.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)
        self.assertEqual(self.pu_player.acumulador_deaths, 1)
        self.assertEqual(self.pu_player2.acumulador_kills, 1)
        self.assertEqual(self.pu_player2.puntos, 0)
        self.assertEqual(self.pu_creator.puntos, 3)

# PUNTOS EXTRA AL GANADOR DE LA MANO

    def test_suma_2_con_una_joya_real(self):
        self.crear_ronda(
            num=1,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "3_JOYAS_REALES",
                PartidaUsuario.ColorJugador.AZUL: "2_OROS",
                PartidaUsuario.ColorJugador.VERDE: "2_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )
        self.crear_ronda(
            num=2,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "4_ESPADAS",
                PartidaUsuario.ColorJugador.AZUL: "3_OROS",
                PartidaUsuario.ColorJugador.VERDE: "3_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )
        self.crear_ronda(
            num=3,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "1_ESPADAS",
                PartidaUsuario.ColorJugador.AZUL: "4_OROS",
                PartidaUsuario.ColorJugador.VERDE: "4_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )

        ronda_service.aux_resolver_ganador_mano(self.partida.id)

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 2+4)

    def test_suma_3_con_dos_joyas_reales(self):
        self.crear_ronda(
            num=1,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "3_JOYAS_REALES",
                PartidaUsuario.ColorJugador.AZUL: "2_OROS",
                PartidaUsuario.ColorJugador.VERDE: "2_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )
        self.crear_ronda(
            num=2,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "4_JOYAS_REALES",
                PartidaUsuario.ColorJugador.AZUL: "3_OROS",
                PartidaUsuario.ColorJugador.VERDE: "3_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )
        self.crear_ronda(
            num=3,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "1_ESPADAS",
                PartidaUsuario.ColorJugador.AZUL: "4_OROS",
                PartidaUsuario.ColorJugador.VERDE: "4_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )

        ronda_service.aux_resolver_ganador_mano(self.partida.id)

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 3+4)

    def test_suma_4_por_carta_unica(self):
        self.crear_ronda(
            num=1,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "DON_DINERO",
                PartidaUsuario.ColorJugador.AZUL: "2_OROS",
                PartidaUsuario.ColorJugador.VERDE: "2_BASTOS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )
        self.crear_ronda(
            num=2,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "1_ESPADAS",
                PartidaUsuario.ColorJugador.AZUL: "3_OROS",
                PartidaUsuario.ColorJugador.VERDE: "3_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )
        self.crear_ronda(
            num=3,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "12_ESPADAS",
                PartidaUsuario.ColorJugador.AZUL: "4_OROS",
                PartidaUsuario.ColorJugador.VERDE: "4_COPAS",
            },
            ganador=PartidaUsuario.ColorJugador.ROJO,
        )

        ronda_service.aux_resolver_ganador_mano(self.partida.id)

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.puntos, 4+4)


# PUNTOS EXTRA FIN DE MANO

    def test_segador_suma_3_por_3_cartas_valiosas(self):
            self.crear_ronda(
                num=1,
                cartas={
                    PartidaUsuario.ColorJugador.ROJO: "SEGADOR",
                    PartidaUsuario.ColorJugador.AZUL: "2_OROS",
                    PartidaUsuario.ColorJugador.VERDE: "2_BASTOS_PUNTIAGUDOS",
                },
                ganador=PartidaUsuario.ColorJugador.VERDE,
            )
            self.crear_ronda(
                num=2,
                cartas={
                    PartidaUsuario.ColorJugador.ROJO: "1_ESPADAS",
                    PartidaUsuario.ColorJugador.AZUL: "3_JOYAS_REALES",
                    PartidaUsuario.ColorJugador.VERDE: "3_COPAS",
                },
                ganador=PartidaUsuario.ColorJugador.ROJO,
            )
            self.crear_ronda(
                num=3,
                cartas={
                    PartidaUsuario.ColorJugador.ROJO: "12_ESPADAS",
                    PartidaUsuario.ColorJugador.AZUL: "4_OROS",
                    PartidaUsuario.ColorJugador.VERDE: "4_VINOS_VIEJOS",
                },
                ganador=PartidaUsuario.ColorJugador.ROJO,
            )
    
            ronda_service.aux_resolver_ganador_mano(self.partida.id)
    
            self.pu_creator.refresh_from_db()
            self.assertEqual(self.pu_creator.puntos, 4+6)


# FUNCIONAMIENTO DE CARTAS QUE ALTERAN GANADOR

    def test_bufon_gana_a_todo_sin_magicas_ni_unicas(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="BUFON",
            azul="2_OROS",
            verde="3_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)

    def test_bufon_no_gana_si_hay_magica(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="BUFON",
            azul="REBELDE",
            verde="2_OROS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.assertNotEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)

    def test_bufon_no_gana_si_hay_unica(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="BUFON",
            azul="DON_DINERO",
            verde="2_OROS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.assertNotEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)

    def test_martirizado_mata_valiosa(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="MARTIRIZADO",
            azul="3_JOYAS_REALES",
            verde="1_ESPADAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.pu_player.acumulador_deaths, 1)
        self.assertEqual(self.pu_creator.acumulador_kills, 1)
        self.assertEqual(self.pu_creator.puntos, 2)

    def test_martirizado_mata_magica(self):
            ronda_nueva = self.jugar_cartas_en_ronda(
                num=1,
                rojo="MARTIRIZADO",
                azul="REBELDE",
                verde="1_ESPADAS",
            )
    
            ronda_service.ganador_ronda(self.partida.id)
    
            ronda_nueva.refresh_from_db()
            self.pu_player.refresh_from_db()
            self.pu_creator.refresh_from_db()
            self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
            self.assertEqual(self.pu_player.acumulador_deaths, 1)
            self.assertEqual(self.pu_creator.acumulador_kills, 1)
            self.assertEqual(self.pu_creator.puntos, 3)

    def test_martirizado_mata_unica(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="MARTIRIZADO",
            azul="DON_DINERO",
            verde="1_ESPADAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.pu_player.acumulador_deaths, 1)
        self.assertEqual(self.pu_creator.acumulador_kills, 1)
        self.assertEqual(self.pu_creator.puntos, 4)

    def test_corruptor_se_apropia_de_muerte_cartas_normales(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="CORRUPTOR",
            azul="7_ESPADAS",
            verde="8_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.assertNotEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.VERDE)
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.pu_creator.puntos, 1)

    def test_corruptor_se_apropia_de_muerte_contra_bastos_punt(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="CORRUPTOR",
            azul="12_BASTOS_PUNTIAGUDOS",
            verde="4_COPAS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.assertNotEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.pu_creator.puntos, 1)

    def test_bastos_punt_contra_ataque_numero(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="5_BASTOS_PUNTIAGUDOS",
            azul="1_COPAS",
            verde="2_OROS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.assertNotEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.pu_player.acumulador_deaths, 1)
        self.assertEqual(self.pu_creator.acumulador_kills, 1)
        self.assertEqual(self.pu_creator.puntos, 1)

    def test_bastos_punt_contra_ataque_figura(self):
        ronda_nueva = self.jugar_cartas_en_ronda(
            num=1,
            rojo="12_BASTOS_PUNTIAGUDOS",
            azul="5_COPAS",
            verde="2_OROS",
        )

        ronda_service.ganador_ronda(self.partida.id)

        ronda_nueva.refresh_from_db()
        self.pu_player.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.assertNotEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)
        self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.pu_player.acumulador_deaths, 1)
        self.assertEqual(self.pu_creator.acumulador_kills, 1)
        self.assertEqual(self.pu_creator.puntos, 2)

    def test_bastos_punt_contra_ataque_as(self):
            ronda_nueva = self.jugar_cartas_en_ronda(
                num=1,
                rojo="1_BASTOS_PUNTIAGUDOS",
                azul="3_COPAS",
                verde="2_OROS",
            )
    
            ronda_service.ganador_ronda(self.partida.id)
    
            ronda_nueva.refresh_from_db()
            self.pu_player.refresh_from_db()
            self.pu_creator.refresh_from_db()
            self.assertNotEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.AZUL)
            self.assertEqual(ronda_nueva.ganador, PartidaUsuario.ColorJugador.ROJO)
            self.assertEqual(self.pu_player.acumulador_deaths, 1)
            self.assertEqual(self.pu_creator.acumulador_kills, 1)
            self.assertEqual(self.pu_creator.puntos, 3)
