from django.db import migrations
from django.utils import timezone


TEST_TORNEOS = [
    {
        "nombre": "Torneo de Prueba",
        "num_jug_fin": 3,
        "num_jug_sem": 3,
        "num_jug_cua": 3,
        "num_jug_oct": None,
        "partidas_longitud": "normal",
        "partidas_cartas_especiales": True,
        "partidas_tickets": True,
        "partidas_tiempo_max_turno": 90,
        "desempate_mayor_punt": True,
        "rango_minimo": "PRINCIPIANTE",
        "rango_maximo": "MAESTRO SUPREMO CELESTIAL",
    },
    {
        "nombre": "Torneo Corto de Prueba",
        "fecha_inicio": timezone.now(),
        "num_jug_fin": 2,
        "num_jug_sem": 2,
        "num_jug_cua": None,
        "num_jug_oct": None,
        "partidas_longitud": "corta",
        "partidas_cartas_especiales": False,
        "partidas_tickets": False,
        "partidas_tiempo_max_turno": 60,
        "desempate_mayor_punt": False,
        "rango_minimo": None,
        "rango_maximo": None,
    },
]

TEST_PARTIDAS_TORNEO = [
    {
        "partida": "Partida 1",
        "torneo": "Torneo Corto de Prueba",
        "fase": "semifinal",
        "lado": 0,
        "pareja": 0,
        "posiciones_finales": {1: 120, 2: 80},
    },
    {
        "partida": "Partida 2",
        "torneo": "Torneo Corto de Prueba",
        "fase": "semifinal",
        "lado": 0,
        "pareja": 0,
        "posiciones_finales": {1: 90, 2: 85},
    },
    {
        "partida": "Partida 3",
        "torneo": "Torneo Corto de Prueba",
        "fase": "final",
        "lado": 0,
        "pareja": 0,
        "posiciones_finales": {},
    },
]

TEST_MEDALLAS = [
    {
        "nombre": "Campeon del Torneo 2026",
        "categoria": "oro",
        "imagen": None,
    },
    {
        "nombre": "Subcampeon del Torneo 2026",
        "categoria": "plata",
        "imagen": None,
    },
    {
        "nombre": "Tercer Puesto del Torneo 2026",
        "categoria": "bronce",
        "imagen": None,
    },
]


def _resolve_rango(rango_model, nombre):
    if not nombre:
        return None
    return rango_model.objects.get(nombre=nombre)


def seed_test_torneos(apps, schema_editor):
    Torneo = apps.get_model("api", "Torneo")
    Rango = apps.get_model("api", "Rango")

    for torneo_spec in TEST_TORNEOS:
        defaults = {
            "fecha_inicio": torneo_spec["fecha_inicio"] if "fecha_inicio" in torneo_spec else None,
            "num_jug_fin": torneo_spec["num_jug_fin"],
            "num_jug_sem": torneo_spec["num_jug_sem"],
            "num_jug_cua": torneo_spec["num_jug_cua"],
            "num_jug_oct": torneo_spec["num_jug_oct"],
            "partidas_longitud": torneo_spec["partidas_longitud"],
            "partidas_cartas_especiales": torneo_spec["partidas_cartas_especiales"],
            "partidas_tickets": torneo_spec["partidas_tickets"],
            "partidas_tiempo_max_turno": torneo_spec["partidas_tiempo_max_turno"],
            "desempate_mayor_punt": torneo_spec["desempate_mayor_punt"],
            "rango_minimo": _resolve_rango(Rango, torneo_spec["rango_minimo"]),
            "rango_maximo": _resolve_rango(Rango, torneo_spec["rango_maximo"]),
        }
        Torneo.objects.update_or_create(nombre=torneo_spec["nombre"], defaults=defaults)


def seed_test_partidas_torneo(apps, schema_editor):
    Partida = apps.get_model("api", "Partida")
    PartidaTorneo = apps.get_model("api", "PartidaTorneo")
    Torneo = apps.get_model("api", "Torneo")

    for partida_torneo_spec in TEST_PARTIDAS_TORNEO:
        partida = Partida.objects.get(nombre=partida_torneo_spec["partida"])
        torneo = Torneo.objects.get(nombre=partida_torneo_spec["torneo"])
        lookup = {
            "partida": partida,
            "torneo": torneo,
            "fase": partida_torneo_spec["fase"],
            "lado": partida_torneo_spec["lado"],
            "pareja": partida_torneo_spec["pareja"],
        }
        PartidaTorneo.objects.update_or_create(
            **lookup,
            defaults={"posiciones_finales": partida_torneo_spec["posiciones_finales"]},
        )


def seed_test_medallas(apps, schema_editor):
    Medalla = apps.get_model("api", "Medalla")

    for medalla_spec in TEST_MEDALLAS:
        Medalla.objects.update_or_create(
            nombre=medalla_spec["nombre"],
            defaults={
                "categoria": medalla_spec["categoria"],
                "imagen": medalla_spec["imagen"],
            },
        )


def unseed_test_medallas(apps, schema_editor):
    Medalla = apps.get_model("api", "Medalla")
    nombres = [medalla["nombre"] for medalla in TEST_MEDALLAS]
    Medalla.objects.filter(nombre__in=nombres).delete()


def unseed_test_partidas_torneo(apps, schema_editor):
    PartidaTorneo = apps.get_model("api", "PartidaTorneo")
    Torneo = apps.get_model("api", "Torneo")
    nombres_torneos = [torneo["nombre"] for torneo in TEST_TORNEOS]
    PartidaTorneo.objects.filter(torneo__nombre__in=nombres_torneos).delete()


def unseed_test_torneos(apps, schema_editor):
    Torneo = apps.get_model("api", "Torneo")
    nombres = [torneo["nombre"] for torneo in TEST_TORNEOS]
    Torneo.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_seed_test_partidas"),
    ]

    operations = [
        migrations.RunPython(seed_test_torneos, reverse_code=unseed_test_torneos),
        migrations.RunPython(seed_test_partidas_torneo, reverse_code=unseed_test_partidas_torneo),
        migrations.RunPython(seed_test_medallas, reverse_code=unseed_test_medallas),
    ]