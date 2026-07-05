import os

from locust import SequentialTaskSet, task

from api.tests.locust_common import AuthenticatedApiUser, unique_suffix


SEED_PRIVATE_CLAVE = os.getenv("LOCUST_PARTIDA_PRIVADA_CLAVE", "claveparaprobartam00")


def _first_partida_id(response):
	items = response.json().get("items", [])
	if not items:
		return None
	return items[0].get("id")


class PartidaPublicaTaskSet(SequentialTaskSet):
	public_partida_id = None
	public_joined = False

	def on_start(self):
		self.public_partida_id = None
		self.public_joined = False

	def _ensure_public_partida(self):
		if self.public_partida_id:
			return self.public_partida_id

		response = self.client.get(
			"/api/partidas/publicas/",
			params={"page": 1, "ordering": "-id"},
			name="/api/partidas/publicas/",
		)
		if response.status_code != 200:
			return None

		self.public_partida_id = _first_partida_id(response)
		return self.public_partida_id

	@task(3)
	def listar_partidas_publicas(self):
		self._ensure_public_partida()

	@task(2)
	def unirse_a_partida_publica(self):
		partida_id = self._ensure_public_partida()
		if not partida_id or self.public_joined:
			return

		response = self.client.post(
			f"/api/partidas/{partida_id}/unirse/",
			name="/api/partidas/[id]/unirse/",
		)
		if response.status_code == 200:
			self.public_joined = True

	@task(2)
	def get_partida_como_jugador_publica(self):
		if not self.public_joined or not self.public_partida_id:
			return

		self.client.get(
			f"/api/partidas/{self.public_partida_id}/jugador/",
			name="/api/partidas/[id]/jugador/",
		)

	@task(2)
	def get_jugadores_partida_publica(self):
		if not self.public_joined or not self.public_partida_id:
			return

		self.client.get(
			f"/api/partidas/{self.public_partida_id}/jugadores/",
			name="/api/partidas/[id]/jugadores/",
		)

	@task(2)
	def get_participacion_publica(self):
		if not self.public_partida_id:
			return

		self.client.get(
			f"/api/partidas/{self.public_partida_id}/participa/",
			name="/api/partidas/[id]/participa/",
		)

	@task(2)
	def toggle_listo_publica(self):
		if not self.public_joined or not self.public_partida_id:
			return

		self.client.put(
			f"/api/partidas/{self.public_partida_id}/toggle-listo/",
			name="/api/partidas/[id]/toggle-listo/",
		)

	@task(2)
	def abandonar_partida_publica(self):
		if not self.public_joined or not self.public_partida_id:
			return

		response = self.client.delete(
			f"/api/partidas/{self.public_partida_id}/abandonar/",
			name="/api/partidas/[id]/abandonar/",
		)
		if response.status_code == 200:
			self.public_joined = False


class PartidaPrivadaTaskSet(SequentialTaskSet):
	private_joined = False
	private_partida_id = None

	def on_start(self):
		self.private_joined = False
		self.private_partida_id = None

	def _ensure_private_partida_id(self):
		if self.private_partida_id:
			return self.private_partida_id

		response = self.client.get(
			f"/api/partidas/{SEED_PRIVATE_CLAVE}/participa/",
			name="/api/partidas/[clave]/participa/",
		)
		if response.status_code != 200:
			return None

		self.private_partida_id = response.json().get("id")
		return self.private_partida_id

	@task(2)
	def unirse_a_partida_privada(self):
		if self.private_joined:
			return

		response = self.client.post(
			f"/api/partidas/{SEED_PRIVATE_CLAVE}/unirse/",
			name="/api/partidas/[clave]/unirse/",
		)
		if response.status_code == 200:
			self.private_joined = True
			self._ensure_private_partida_id()

	@task(2)
	def get_partida_como_jugador_privada(self):
		if not self.private_joined:
			return
		partida_id = self._ensure_private_partida_id()
		if not partida_id:
			return

		self.client.get(
			f"/api/partidas/{partida_id}/jugador/",
			name="/api/partidas/[id]/jugador/",
		)

	@task(2)
	def get_jugadores_partida_privada(self):
		if not self.private_joined:
			return
		partida_id = self._ensure_private_partida_id()
		if not partida_id:
			return

		self.client.get(
			f"/api/partidas/{partida_id}/jugadores/",
			name="/api/partidas/[id]/jugadores/",
		)

	@task(2)
	def get_participacion_privada(self):
		if not self.private_joined:
			return

		self.client.get(
			f"/api/partidas/{SEED_PRIVATE_CLAVE}/participa/",
			name="/api/partidas/[clave]/participa/",
		)

	@task(2)
	def toggle_listo_privada(self):
		if not self.private_joined:
			return

		self.client.put(
			f"/api/partidas/{SEED_PRIVATE_CLAVE}/toggle-listo/",
			name="/api/partidas/[clave]/toggle-listo/",
		)

	@task(2)
	def abandonar_partida_privada(self):
		if not self.private_joined:
			return

		response = self.client.delete(
			f"/api/partidas/{SEED_PRIVATE_CLAVE}/abandonar/",
			name="/api/partidas/[clave]/abandonar/",
		)
		if response.status_code == 200:
			self.private_joined = False


class PartidaCreadorTaskSet(SequentialTaskSet):
	created_partida_id = None
	created_partida_nombre = None
	created_partida_clave = None

	def on_start(self):
		self.created_partida_id = None
		self.created_partida_nombre = None
		self.created_partida_clave = None
		self._crear_partida_privada()

	def _crear_partida_privada(self):
		suffix = unique_suffix()
		nombre = f"locust_partida_{suffix}"
		clave = f"locust{suffix}"
		payload = {
			"nombre": nombre,
			"num_jugadores": 2,
			"privada": True,
			"clave": clave,
			"longitud": "normal",
			"cartas_especiales": True,
			"tickets": True,
			"tiempo_max_turno": 90,
			"rango_minimo_id": None,
			"rango_maximo_id": None,
		}

		response = self.client.post(
			"/api/partidas/crear/",
			json=payload,
			headers=self.user._auth_headers(),
			name="/api/partidas/crear/",
		)
		if response.status_code != 201:
			return None

		self.created_partida_id = response.json().get("id")
		self.created_partida_nombre = nombre
		self.created_partida_clave = clave
		return self.created_partida_id

	@task(3)
	def editar_partida_privada(self):
		if not self.created_partida_id:
			return

		suffix = unique_suffix()
		payload = {
			"nombre": f"{self.created_partida_nombre}_{suffix}",
			"num_jugadores": 3,
			"privada": True,
			"clave": self.created_partida_clave,
			"longitud": "normal",
			"cartas_especiales": True,
			"tickets": True,
			"tiempo_max_turno": 90,
			"rango_minimo_id": None,
			"rango_maximo_id": None,
		}

		response = self.client.put(
			f"/api/partidas/{self.created_partida_id}/editar/",
			json=payload,
			headers=self.user._auth_headers(),
			name="/api/partidas/[id]/editar/",
		)
		if response.status_code == 200:
			self.created_partida_nombre = payload["nombre"]

	@task(2)
	def get_partida_como_jugador(self):
		if not self.created_partida_id:
			return

		self.client.get(
			f"/api/partidas/{self.created_partida_id}/jugador/",
			name="/api/partidas/[id]/jugador/",
		)

	@task(2)
	def get_jugadores_partida(self):
		if not self.created_partida_id:
			return

		self.client.get(
			f"/api/partidas/{self.created_partida_id}/jugadores/",
			name="/api/partidas/[id]/jugadores/",
		)

	@task(2)
	def get_participacion_partida(self):
		if not self.created_partida_id:
			return

		self.client.get(
			f"/api/partidas/{self.created_partida_id}/participa/",
			name="/api/partidas/[id]/participa/",
		)

	@task(1)
	def expulsar_jugador(self):
		if not self.created_partida_id:
			return

		self.client.delete(
			f"/api/partidas/{self.created_partida_id}/expulsar-jugador/999999/",
			name="/api/partidas/[id]/expulsar-jugador/[id]/",
		)

	@task(1)
	def iniciar_partida(self):
		if not self.created_partida_id:
			return

		self.client.put(
			f"/api/partidas/{self.created_partida_id}/iniciar/",
			name="/api/partidas/[id]/iniciar/",
		)


class PartidaPublicaLoad(AuthenticatedApiUser):
	tasks = [PartidaPublicaTaskSet]


class PartidaPrivadaLoad(AuthenticatedApiUser):
	tasks = [PartidaPrivadaTaskSet]


class PartidaCreadorLoad(AuthenticatedApiUser):
	tasks = [PartidaCreadorTaskSet]