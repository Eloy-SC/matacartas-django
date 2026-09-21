from django.db import migrations


TEST_LOGROS = [
    {
        "nombre": "Prueba puntos ganados",
        "descripcion": "Gana 15 puntos en partida.",
        "requisitos": [("puntos_ganados_partida", False, 15)],
    },
    {
        "nombre": "Prueba puntuacion acumulada",
        "descripcion": "Logro de prueba para puntuacion acumulada.",
        "requisitos": [("puntuacion_acumulada", False, 100)],
    },
    {
        "nombre": "Prueba puntos mercader",
        "descripcion": "Gana 4 puntos con el Mercader.",
        "requisitos": [("puntos_ganados_mercader", False, 4)],
    },
    {
        "nombre": "Prueba puntos rebelde",
        "descripcion": "Gana 4 puntos con el Rebelde.",
        "requisitos": [("puntos_ganados_rebelde", False, 4)],
    },
    {
        "nombre": "Prueba puntos segador",
        "descripcion": "Gana 4 puntos con el Segador.",
        "requisitos": [("puntos_ganados_segador", False, 4)],
    },
    {
        "nombre": "Prueba victimas segador",
        "descripcion": "Elimina 4 cartas valiosas con el Segador.",
        "requisitos": [("cartas_victimas_segador", False, 4)],
    },
    {
        "nombre": "Prueba puntos joyas reales",
        "descripcion": "Gana 4 puntos con joyas reales.",
        "requisitos": [("puntos_ganados_joyas_reales", False, 4)],
    },
    {
        "nombre": "Prueba puntos vinos viejos",
        "descripcion": "Gana 4 puntos con vinos viejos.",
        "requisitos": [("puntos_ganados_vinos_viejos", False, 4)],
    },
    {
        "nombre": "Prueba muertes corruptor",
        "descripcion": "Corrompe una muerte con el Corruptor.",
        "requisitos": [("muertes_corrompidas_corruptor", False, 1)],
    },
    {
        "nombre": "Prueba tumbas saqueador",
        "descripcion": "Saquea una tumba con el Saqueador.",
        "requisitos": [("tumbas_saqueadas_saqueador", False, 1)],
    },
    {
        "nombre": "Prueba partidas ganadas",
        "descripcion": "Gana una partida.",
        "requisitos": [("partidas_ganadas", False, 1)],
    },
    {
        "nombre": "Prueba cartas kills",
        "descripcion": "Mata 2 cartas rivales.",
        "requisitos": [("cartas_kills", False, 2)],
    },
    {
        "nombre": "Prueba cartas deaths",
        "descripcion": "Pierde 1 ronda por muerte.",
        "requisitos": [("cartas_deaths", False, 1)],
    },
    {
        "nombre": "Prueba rondas ganadas",
        "descripcion": "Gana 5 rondas.",
        "requisitos": [("rondas_ganadas", False, 5)],
    },
    {
        "nombre": "Prueba rondas comodin",
        "descripcion": "Gana 1 ronda con comodin.",
        "requisitos": [("rondas_comodin_ganadas", False, 1)],
    },
    {
        "nombre": "Prueba manos ganadas",
        "descripcion": "Gana 2 manos.",
        "requisitos": [("manos_ganadas", False, 2)],
    },
    {
        "nombre": "Prueba retiradas",
        "descripcion": "Retírate 2 veces.",
        "requisitos": [("retiradas", False, 2)],
    },
    {
        "nombre": "Prueba manos carta unica",
        "descripcion": "Gana una mano con una carta única.",
        "requisitos": [("manos_ganadas_unica", False, 1)],
    },
    {
        "nombre": "Prueba contraataques bastos",
        "descripcion": "Contraataca una muerte con una carta de bastos puntiagudos.",
        "requisitos": [("contraataques_bastos_punt", False, 1)],
    },
    {
        "nombre": "Prueba tickets usados",
        "descripcion": "Usa 1 ticket.",
        "requisitos": [("tickets_usados", False, 1)],
    },
    {
        "nombre": "Prueba logro compuesto A",
        "descripcion": "Gana 2 partidas y 20 puntos en partida.",
        "requisitos": [
            ("puntos_ganados_partida", False, 20),
            ("partidas_ganadas", False, 2),
        ],
    },
    {
        "nombre": "Prueba logro compuesto B",
        "descripcion": "Mata 3 cartas rivales y gana 3 rondas.",
        "requisitos": [
            ("cartas_kills", False, 3),
            ("rondas_ganadas", False, 3),
        ],
    },
    {
        "nombre": "Prueba logro compuesto C",
        "descripcion": "Obten dos puntos con el Mercader y dos puntos con el Rebelde.",
        "requisitos": [
            ("puntos_ganados_mercader", False, 2),
            ("puntos_ganados_rebelde", False, 2),
        ],
    },
    {
        "nombre": "Prueba logro compuesto triple",
        "descripcion": "Gana 2 manos y 2 rondas comodín y usa 2 tickets.",
        "requisitos": [
            ("manos_ganadas", False, 2),
            ("rondas_comodin_ganadas", False, 2),
            ("tickets_usados", False, 2),
        ],
    },
    {
        "nombre": "Prueba una partida puntos",
        "descripcion": "Gana 10 puntos en una sola partida.",
        "requisitos": [("puntos_ganados_partida", True, 10)],
    },
    {
        "nombre": "Prueba una partida kills",
        "descripcion": "Mata 5 cartas rivales en una sola partida.",
        "requisitos": [("cartas_kills", True, 5)],
    },
    {
        "nombre": "Prueba una partida manos",
        "descripcion": "Gana 3 manos en una sola partida.",
        "requisitos": [("manos_ganadas", True, 3)],
    },
]


def seed_test_logros(apps, schema_editor):
    Logro = apps.get_model("api", "Logro")
    RequisitoLogro = apps.get_model("api", "RequisitoLogro")

    for logro_spec in TEST_LOGROS:
        logro, _ = Logro.objects.update_or_create(
            nombre=logro_spec["nombre"],
            defaults={
                "descripcion": logro_spec["descripcion"],
                "imagen": None,
                "oculto": False,
            },
        )
        requisitos = logro_spec["requisitos"]
        RequisitoLogro.objects.filter(logro=logro).exclude(
            requisito__in=[requisito[0] for requisito in requisitos]
        ).delete()
        for requisito, una_partida, valor_necesario in requisitos:
            RequisitoLogro.objects.update_or_create(
                logro=logro,
                requisito=requisito,
                defaults={
                    "una_partida": una_partida,
                    "valor_necesario": valor_necesario,
                },
            )


def unseed_test_logros(apps, schema_editor):
    Logro = apps.get_model("api", "Logro")
    nombres = [logro["nombre"] for logro in TEST_LOGROS]
    Logro.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0004_seed_test_torneos"),
    ]

    operations = [
        migrations.RunPython(seed_test_logros, reverse_code=unseed_test_logros),
    ]
