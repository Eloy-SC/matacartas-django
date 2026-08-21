from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.mano import Mano
from api.models.partida import Partida
from api.models.partida_usuario import PartidaUsuario
from api.models.ronda import Ronda
from api.services import mano_service
from api.utils.funciones_aux import aux_siguiente_turno


class ManoServiceTests(TestCase):
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
            nombre="PartidaManoService",
            num_jugadores=2,
            privada=False,
            clave=None,
            longitud=Partida.LongitudPartida.NORMAL,
            cartas_especiales=True,
            tickets=True,
            tiempo_max_turno=90,
            baraja=["CARTA_1", "CARTA_2", "CARTA_3", "CARTA_4", "CARTA_5", "CARTA_6", "CARTA_7", "CARTA_8"],
            disposicion_jugadores=[PartidaUsuario.ColorJugador.ROJO, PartidaUsuario.ColorJugador.AZUL],
            turno_actual=PartidaUsuario.ColorJugador.ROJO,
        )

        self.pu_creator = PartidaUsuario.objects.create(
            partida=self.partida,
            usuario=self.creator,
            creador=True,
            listo=True,
            color=PartidaUsuario.ColorJugador.ROJO,
            cartas=[],
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
        self.ronda_cambios = Ronda.objects.create(mano=self.mano, num=0, cartas={}, cambios=0)

    def test_get_mesa_requires_membership(self):
        with self.assertRaises(PermissionError):
            mano_service.get_mesa(self.outsider, self.partida.id)

    def test_get_mesa_returns_dto(self):
        mesa = mano_service.get_mesa(self.creator, self.partida.id)
        self.assertEqual(mesa.partida.partida_id, self.partida.id)
        self.assertEqual(mesa.jugador.jugador_id, self.creator.id)
        self.assertEqual(len(mesa.contrincantes), 1)
        self.assertEqual(mesa.contrincantes[0].nombre, "Player")

    def test_repartir_cartas_distributes_cards_and_sets_turno(self):
        mano_service.repartir_cartas(self.creator, self.partida.id)

        self.partida.refresh_from_db()
        self.pu_creator.refresh_from_db()
        self.pu_player.refresh_from_db()

        self.assertEqual(self.partida.turno_actual, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(len(self.pu_creator.cartas), 4)
        self.assertEqual(len(self.pu_player.cartas), 4)

    def test_jugador_quiere_cambiar_advances_turn_and_marks_round(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.AZUL
        self.partida.save(update_fields=["turno_actual"])

        mano_service.jugador_quiere_cambiar(self.player, self.partida.id)

        self.partida.refresh_from_db()
        self.ronda_cambios.refresh_from_db()
        self.assertEqual(self.partida.turno_actual, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.ronda_cambios.cambios, 1)

    def test_jugador_no_quiere_cambiar_finalizes_change_round(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.AZUL
        self.partida.save(update_fields=["turno_actual"])

        mano_service.jugador_no_quiere_cambiar(self.player, self.partida.id)

        self.partida.refresh_from_db()
        self.ronda_cambios.refresh_from_db()
        self.assertEqual(self.partida.turno_actual, PartidaUsuario.ColorJugador.ROJO)
        self.assertEqual(self.ronda_cambios.cambios, 2)

    def test_aux_siguiente_turno_skips_current_abandoned_player(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.ROJO
        self.partida.save(update_fields=["turno_actual"])
        self.pu_creator.abandono = True
        self.pu_creator.save(update_fields=["abandono"])

        aux_siguiente_turno(self.partida)

        self.partida.refresh_from_db()
        self.assertEqual(self.partida.turno_actual, PartidaUsuario.ColorJugador.AZUL)

    def test_aux_siguiente_turno_wraps_when_next_player_abandoned(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.ROJO
        self.partida.save(update_fields=["turno_actual"])
        self.pu_player.abandono = True
        self.pu_player.save(update_fields=["abandono"])

        aux_siguiente_turno(self.partida)

        self.partida.refresh_from_db()
        self.assertEqual(self.partida.turno_actual, PartidaUsuario.ColorJugador.ROJO)

    def test_aux_siguiente_turno_raises_when_all_players_abandoned(self):
        self.pu_creator.abandono = True
        self.pu_creator.save(update_fields=["abandono"])
        self.pu_player.abandono = True
        self.pu_player.save(update_fields=["abandono"])

        with self.assertRaisesRegex(ValueError, "No hay jugadores activos"):
            aux_siguiente_turno(self.partida)

    def test_cambiar_cartas_swaps_cards_and_refills_hand(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.ROJO
        self.partida.save(update_fields=["turno_actual"])
        self.pu_creator.cartas = ["CARTA_A", "CARTA_B", "CARTA_C", "CARTA_D"]
        self.pu_creator.save(update_fields=["cartas"])

        mano_service.cambiar_cartas(self.creator, self.partida.id, ["CARTA_A", "CARTA_B"])

        self.pu_creator.refresh_from_db()
        self.assertEqual(len(self.pu_creator.cartas), 4)
        self.assertNotIn("CARTA_A", self.pu_creator.cartas)
        self.assertNotIn("CARTA_B", self.pu_creator.cartas)

    def test_elegir_carta_comodin_sets_selected_card(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.ROJO
        self.partida.save(update_fields=["turno_actual"])
        self.pu_creator.cartas = ["MONEDERO_PECULIAR", "CARTA_B", "CARTA_C", "CARTA_D"]
        self.pu_creator.save(update_fields=["cartas"])

        mano_service.elegir_carta_comodin(self.creator, self.partida.id, "MONEDERO_PECULIAR")

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.carta_comodin, "MONEDERO_PECULIAR")
        self.assertNotIn("MONEDERO_PECULIAR", self.pu_creator.cartas)

    def test_siguiente_mano_does_not_duplicate_comodin_if_already_in_hand(self):
        self.partida.turno_actual = PartidaUsuario.ColorJugador.ROJO
        self.partida.save(update_fields=["turno_actual"])
        self.pu_creator.cartas = ["MONEDERO_PECULIAR", "CARTA_B", "CARTA_C"]
        self.pu_creator.carta_comodin = "MONEDERO_PECULIAR"
        self.pu_creator.save(update_fields=["cartas", "carta_comodin"])
        
        self.mano.ganador = self.pu_creator.color
        self.mano.save(update_fields=["ganador"])

        mano_service.siguiente_mano(self.creator, self.partida.id)

        self.pu_creator.refresh_from_db()
        self.assertEqual(self.pu_creator.cartas.count("MONEDERO_PECULIAR"), 1)
        self.assertIsNone(self.pu_creator.carta_comodin)

    def test_get_datos_carta_returns_catalog_data(self):
        datos = mano_service.get_datos_carta(self.creator, "2_OROS", self.partida.id)

        self.assertEqual(datos["nombre"], "2_OROS")
        self.assertIn("fuerza", datos)
        self.assertIn("riqueza", datos)
        self.assertIn("tipo", datos)

    def test_siguiente_mano_creates_new_mano(self):
        self.mano.ganador = self.pu_creator.color
        self.mano.save(update_fields=["ganador"])
        with patch("api.services.mano_service.repartir_cartas") as repartir_mock:
            mano_service.siguiente_mano(self.creator, self.partida.id)

        repartir_mock.assert_called_once_with(self.creator, self.partida.id)
        self.assertEqual(Mano.objects.filter(partida=self.partida).count(), 2)
