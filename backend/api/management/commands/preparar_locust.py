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

        for i in range(1, 11):
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

        for i in range(5):
            partida, _ = Partida.objects.get_or_create(
                nombre=f"partida_empezada_{i + 1}",
                defaults={
                    "num_jugadores": 2,
                    "privada": False,
                    "clave": None,
                    "longitud": Partida.LongitudPartida.NORMAL,
                    "cartas_especiales": True,
                    "tickets": True,
                    "tiempo_max_turno": 90,
                    "fecha_inicio": timezone.now(),
                    "disposicion_jugadores": [
                        PartidaUsuario.ColorJugador.ROJO,
                        PartidaUsuario.ColorJugador.AZUL,
                    ],
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

            usuario_rojo = usuarios[i * 2]
            usuario_azul = usuarios[i * 2 + 1]

            jugador_rojo, _ = PartidaUsuario.objects.get_or_create(
                partida=partida,
                usuario=usuario_rojo,
                defaults={
                    "creador": True,
                    "listo": True,
                    "color": PartidaUsuario.ColorJugador.ROJO,
                    "cartas": [
                        "1_OROS",
                        "2_COPAS",
                        "3_ESPADAS",
                    ],
                },
            )

            jugador_azul, _ = PartidaUsuario.objects.get_or_create(
                partida=partida,
                usuario=usuario_azul,
                defaults={
                    "creador": False,
                    "listo": True,
                    "color": PartidaUsuario.ColorJugador.AZUL,
                    "cartas": [
                        "4_OROS",
                        "5_COPAS",
                        "6_ESPADAS",
                    ],
                },
            )

            # Por si los objetos ya existían y queremos
            # garantizar el estado de las cartas.
            jugador_rojo.cartas = [
                "1_OROS",
                "2_COPAS",
                "3_ESPADAS",
            ]
            jugador_rojo.save(update_fields=["cartas"])

            jugador_azul.cartas = [
                "4_OROS",
                "5_COPAS",
                "6_ESPADAS",
            ]
            jugador_azul.save(update_fields=["cartas"])

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

            Ronda.objects.get_or_create(
                mano=mano,
                num=1,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Datos de Locust preparados correctamente"
            )
        )