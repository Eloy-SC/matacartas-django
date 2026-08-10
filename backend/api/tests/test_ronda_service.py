from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.mano import Mano
from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.models.ronda import Ronda
from api.services import ronda_service


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
        self.outsider = UserModel.objects.create_user(
            username="outsider",
            password="outsider-pass-123",
            email="outsider@example.com",
            nombre="Outsider",
        )

        self.partida = Partida.objects.create(
            nombre="PartidaRondaService",
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

    def test_aux_get_carta_mayor_fuerza_prefers_bufon(self):
        self.ronda.cartas = {
            PartidaUsuario.ColorJugador.ROJO: "BUFON",
            PartidaUsuario.ColorJugador.AZUL: "2_OROS",
        }
        self.ronda.save(update_fields=["cartas"])

        carta = ronda_service.aux_get_carta_mayor_fuerza(self.partida.id)
        self.assertEqual(carta, "BUFON")

    def test_aux_asignar_puntos_extra_final_mano_applies_all_bonus_paths(self):
        Ronda.objects.create(
            mano=self.mano,
            num=2,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "2_BASTOS",
                PartidaUsuario.ColorJugador.AZUL: "REBELDE",
            },
            cambios=2,
        )
        Ronda.objects.create(
            mano=self.mano,
            num=3,
            cartas={
                PartidaUsuario.ColorJugador.ROJO: "SEGADOR",
                PartidaUsuario.ColorJugador.AZUL: "2_BASTOS_PUNTIAGUDOS",
            },
            cambios=2,
        )
        self.ronda.cartas = {
            PartidaUsuario.ColorJugador.ROJO: "MERCADER",
            PartidaUsuario.ColorJugador.AZUL: "2_OROS",
        }
        self.ronda.save(update_fields=["cartas"])

        ronda_service.aux_asignar_puntos_extra_final_mano(self.partida.id)

        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()

        self.assertEqual(self.pu_creator.puntos, 3)
        self.assertEqual(self.pu_player.puntos, 2)
