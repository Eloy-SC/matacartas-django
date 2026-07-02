from django.db import migrations


TEST_PARTIDAS = [
	{
		"nombre": "p",
		"num_jugadores": 2,
		"longitud": "corta",
		"cartas_especiales": True,
		"tickets": True,
		"tiempo_max_turno": 60,
		"rango_minimo": None,
		"rango_maximo": None,
	},
	{
		"nombre": "Partida con Nombre Increíblemente Largoo",
		"num_jugadores": 3,
		"longitud": "larga",
		"cartas_especiales": True,
		"tickets": True,
		"tiempo_max_turno": 60,
		"rango_minimo": None,
		"rango_maximo": None,
	},
	{
		"nombre": "Partida Tiempo Minimo",
		"num_jugadores": 4,
		"longitud": "corta",
		"cartas_especiales": True,
		"tickets": True,
		"tiempo_max_turno": 20,
		"rango_minimo": None,
		"rango_maximo": None,
	},
	{
		"nombre": "Partida Tiempo Maximo",
		"num_jugadores": 5,
		"longitud": "larga",
		"cartas_especiales": True,
		"tickets": True,
		"tiempo_max_turno": 180,
		"rango_minimo": None,
		"rango_maximo": None,
	},
	{
		"nombre": "Partida 1",
		"num_jugadores": 6,
		"longitud": "normal",
		"cartas_especiales": False,
		"tickets": False,
		"tiempo_max_turno": 60,
		"rango_minimo": "PRINCIPIANTE",
		"rango_maximo": "EXPERIMENTADO",
	},
	{
		"nombre": "Partida 2",
		"num_jugadores": 4,
		"longitud": "normal",
		"cartas_especiales": False,
		"tickets": False,
		"tiempo_max_turno": 60,
		"rango_minimo": "VETERANO",
		"rango_maximo": "Z",
	},
	{
		"nombre": "Partida 3",
		"num_jugadores": 5,
		"longitud": "larga",
		"cartas_especiales": False,
		"tickets": False,
		"tiempo_max_turno": 60,
		"rango_minimo": "MAESTRO",
		"rango_maximo": "MAESTRO SUPREMO CELESTIAL",
	},
	{
		"nombre": "Partida Privada Clave Min",
		"num_jugadores": 4,
		"longitud": "normal",
		"privada": True,
		"clave": "c",
		"cartas_especiales": False,
		"tickets": False,
		"tiempo_max_turno": 60,
		"rango_minimo": None,
		"rango_maximo": None,
	},
	{
		"nombre": "Partida Privada Clave Max",
		"num_jugadores": 4,
		"longitud": "normal",
		"privada": True,
		"clave": "claveparaprobartam00",
		"cartas_especiales": False,
		"tickets": False,
		"tiempo_max_turno": 60,
		"rango_minimo": None,
		"rango_maximo": None,
	},
]


def _resolve_rango(rango_model, nombre):
	if not nombre:
		return None
	return rango_model.objects.filter(nombre=nombre).first()


def seed_test_partidas(apps, schema_editor):
	Partida = apps.get_model("api", "Partida")
	Rango = apps.get_model("api", "Rango")

	for partida_spec in TEST_PARTIDAS:
		defaults = {
			"num_jugadores": partida_spec["num_jugadores"],
			"privada": partida_spec.get("privada", False),
			"clave": partida_spec.get("clave", None),
			"longitud": partida_spec["longitud"],
			"cartas_especiales": partida_spec["cartas_especiales"],
			"tickets": partida_spec["tickets"],
			"tiempo_max_turno": partida_spec["tiempo_max_turno"],
			"rango_minimo": _resolve_rango(Rango, partida_spec.get("rango_minimo")),
			"rango_maximo": _resolve_rango(Rango, partida_spec.get("rango_maximo")),
		}

		Partida.objects.update_or_create(nombre=partida_spec["nombre"], defaults=defaults)


def unseed_test_partidas(apps, schema_editor):
	Partida = apps.get_model("api", "Partida")
	nombres = [partida["nombre"] for partida in TEST_PARTIDAS]
	Partida.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):
	dependencies = [
		("api", "0002_seed_test_users"),
	]

	operations = [
		migrations.RunPython(seed_test_partidas, reverse_code=unseed_test_partidas),
	]
