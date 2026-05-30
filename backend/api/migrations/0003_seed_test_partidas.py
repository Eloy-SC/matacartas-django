from django.db import migrations


TEST_PARTIDAS = [
	{
		"nombre": "Partida 01",
		"num_jugadores": 2,
		"longitud": "corta",
		"cartas_invencibles": True,
		"tiempo_max_turno": 60,
		"rango_minimo": "Novato",
		"rango_maximo": "Experimentado",
	},
	{
		"nombre": "Partida 02",
		"num_jugadores": 3,
		"longitud": "normal",
		"cartas_invencibles": True,
		"tiempo_max_turno": 90,
		"rango_minimo": "Novato",
		"rango_maximo": "Veterano",
	},
	{
		"nombre": "Partida 03",
		"num_jugadores": 4,
		"longitud": "larga",
		"cartas_invencibles": False,
		"tiempo_max_turno": 120,
		"rango_minimo": "Experimentado",
		"rango_maximo": "Veterano",
	},
	{
		"nombre": "Partida 04",
		"num_jugadores": 2,
		"longitud": "corta",
		"cartas_invencibles": True,
		"tiempo_max_turno": 45,
		"rango_minimo": "Novato",
		"rango_maximo": "Maestro",
	},
	{
		"nombre": "Partida 05",
		"num_jugadores": 5,
		"longitud": "normal",
		"cartas_invencibles": True,
		"tiempo_max_turno": 90,
		"rango_minimo": "Experimentado",
		"rango_maximo": "Maestro",
	},
	{
		"nombre": "Partida 06",
		"num_jugadores": 6,
		"longitud": "larga",
		"cartas_invencibles": False,
		"tiempo_max_turno": 120,
		"rango_minimo": "Veterano",
		"rango_maximo": "Gran capitan",
	},
	{
		"nombre": "Partida 07",
		"num_jugadores": 3,
		"longitud": "corta",
		"cartas_invencibles": True,
		"tiempo_max_turno": 75,
		"rango_minimo": "Novato",
		"rango_maximo": "Gran capitan",
	},
	{
		"nombre": "Partida 08",
		"num_jugadores": 4,
		"longitud": "normal",
		"cartas_invencibles": True,
		"tiempo_max_turno": 90,
		"rango_minimo": "Novato",
		"rango_maximo": "Veterano",
	},
	{
		"nombre": "Partida 09",
		"num_jugadores": 2,
		"longitud": "larga",
		"cartas_invencibles": False,
		"tiempo_max_turno": 120,
		"rango_minimo": "Maestro",
		"rango_maximo": "Gran capitan",
	},
	{
		"nombre": "Partida 10",
		"num_jugadores": 5,
		"longitud": "corta",
		"cartas_invencibles": True,
		"tiempo_max_turno": 60,
		"rango_minimo": "Novato",
		"rango_maximo": "Maestro",
	},
	{
		"nombre": "Partida 11",
		"num_jugadores": 6,
		"longitud": "normal",
		"cartas_invencibles": True,
		"tiempo_max_turno": 90,
		"rango_minimo": "Experimentado",
		"rango_maximo": "Gran capitan",
	},
	{
		"nombre": "Partida 12",
		"num_jugadores": 2,
		"longitud": "corta",
		"cartas_invencibles": True,
		"tiempo_max_turno": 45,
		"rango_minimo": None,
		"rango_maximo": None,
	},
	{
		"nombre": "Partida 13",
		"num_jugadores": 3,
		"longitud": "normal",
		"cartas_invencibles": True,
		"tiempo_max_turno": 90,
		"rango_minimo": "Novato",
		"rango_maximo": "Novato",
	},
	{
		"nombre": "Partida 14",
		"num_jugadores": 4,
		"longitud": "larga",
		"cartas_invencibles": False,
		"tiempo_max_turno": 120,
		"rango_minimo": "Veterano",
		"rango_maximo": "Veterano",
	},
	{
		"nombre": "Partida 15",
		"num_jugadores": 5,
		"longitud": "normal",
		"cartas_invencibles": True,
		"tiempo_max_turno": 90,
		"rango_minimo": "Experimentado",
		"rango_maximo": "Maestro",
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
			"privada": False,
			"clave": None,
			"longitud": partida_spec["longitud"],
			"cartas_invencibles": partida_spec["cartas_invencibles"],
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
