from django.utils import timezone

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from ...models.mano import Mano
from ...models.partida import Partida
from ...models.partida_usuario import PartidaUsuario
from ...models.ronda import Ronda


class Command(BaseCommand):
    help = "Prepara los datos necesarios para las pruebas de Locust"

    def handle(self, *args, **options):
        Partida.objects.filter(
            nombre__startswith="partida_empezada_"
        ).delete()

        UserModel = get_user_model()

        UserModel.objects.filter(
            username__startswith="locust_player_"
        ).delete()

        # ==================================================
        # USUARIO ADMINISTRADOR
        # ==================================================

        admin, _ = UserModel.objects.get_or_create(
            username="locust_user",
            defaults={
                "email": "locust@test.com",
                "nombre": "Locust User",
                "is_staff": True,
                "email_verificado": True,
            },
        )

        admin.set_password("locust_password")
        admin.save()

        # ==================================================
        # CREAR USUARIOS DE PRUEBA
        # ==================================================

        usuarios = []

        for i in range(1, 33):
            usuario, _ = UserModel.objects.get_or_create(
                username=f"locust_player_{i}",
                defaults={
                    "email": f"locust_player_{i}@test.com",
                    "nombre": f"Locust Player {i}",
                    "is_staff": False,
                    "email_verificado": True,
                },
            )

            usuario.set_password(f"locust_password_{i}")
            usuario.save()

            usuarios.append(usuario)

        # ==================================================
        # CREAR PARTIDAS EMPEZADAS
        # ==================================================

        colores = [
            PartidaUsuario.ColorJugador.ROJO,
            PartidaUsuario.ColorJugador.AZUL,
            PartidaUsuario.ColorJugador.VERDE,
            PartidaUsuario.ColorJugador.AMARILLO,
        ]

        cartas_por_jugador = [
            ["1_OROS", "2_OROS", "3_OROS"],
            ["1_COPAS", "2_COPAS", "3_COPAS"],
            ["1_ESPADAS", "2_ESPADAS", "3_ESPADAS"],
            ["1_BASTOS", "2_BASTOS", "3_BASTOS"],
        ]

        for i in range(8):
            partida, _ = Partida.objects.get_or_create(
                nombre=f"partida_empezada_{i + 1}",
                defaults={
                    "num_jugadores": 4,
                    "privada": False,
                    "clave": None,
                    "longitud": Partida.LongitudPartida.NORMAL,
                    "cartas_especiales": True,
                    "tickets": True,
                    "tiempo_max_turno": 90,
                    "fecha_inicio": timezone.now(),
                    "disposicion_jugadores": colores,
                    "turno_actual": PartidaUsuario.ColorJugador.ROJO,
                },
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Creada {partida.nombre} con ID {partida.id}"
                )
            )

            # ----------------------------------------------
            # USUARIOS DE LA PARTIDA
            # ----------------------------------------------

            for jugador_index in range(4):
                jugador, _ = PartidaUsuario.objects.get_or_create(
                    partida=partida,
                    usuario=usuarios[i * 4 + jugador_index],
                    defaults={
                        "creador": jugador_index == 0,
                        "listo": True,
                        "color": colores[jugador_index],
                        "cartas": cartas_por_jugador[jugador_index],
                    },
                )
                jugador.creador = jugador_index == 0
                jugador.listo = True
                jugador.color = colores[jugador_index]
                jugador.cartas = cartas_por_jugador[jugador_index]
                jugador.abandono = False
                jugador.retirado = False
                jugador.save(update_fields=["creador", "listo", "color", "cartas", "abandono", "retirado"])

            # ----------------------------------------------
            # MANO
            # ----------------------------------------------

            mano, _ = Mano.objects.get_or_create(
                partida=partida,
                num=1,
            )

            # ----------------------------------------------
            # RONDA
            # ----------------------------------------------

            Ronda.objects.update_or_create(
                mano=mano,
                num=0,
                defaults={"cartas": {}, "cambios": 0},
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Datos de Locust preparados correctamente"
            )
        )