from locust import SequentialTaskSet, task

from api.tests.locust_common import AuthenticatedApiUser


def _first_partida_id(response):
	items = response.json().get("items", [])
	if not items:
		return None
	return items[0].get("id")


class ManoTaskSet(SequentialTaskSet):
	partida_id = None
	joined = False

	def on_start(self):
		self.partida_id = None
		self.joined = False
		self._ensure_joined_partida()

	def _ensure_joined_partida(self):
		if self.joined and self.partida_id:
			return self.partida_id

		response = self.client.get(
			"/api/partidas/publicas/",
			params={"page": 1, "ordering": "-id"},
			name="/api/partidas/publicas/",
		)
		partida_id = _first_partida_id(response)
		if not partida_id:
			return None

		join_response = self.client.post(
			f"/api/partidas/{partida_id}/unirse/",
			headers=self.user._auth_headers(),
			name="/api/partidas/[id]/unirse/",
		)
		if join_response.status_code == 200:
			self.joined = True
			self.partida_id = partida_id
		return self.partida_id

	@task(3)
	def get_mesa(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.get(
			f"/api/partida/{partida_id}/mano/mesa/",
			name="/api/partida/[id]/mano/mesa/",
		)

	@task(2)
	def get_datos_carta(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.get(
			f"/api/partida/{partida_id}/mano/datos-carta/",
			params={"carta": "2_OROS"},
			name="/api/partida/[id]/mano/datos-carta/",
		)

	@task(1)
	def repartir_cartas(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.put(
			f"/api/partida/{partida_id}/mano/repartir/",
			headers=self.user._auth_headers(),
			name="/api/partida/[id]/mano/repartir/",
		)

	@task(1)
	def jugador_quiere_cambiar(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.put(
			f"/api/partida/{partida_id}/mano/quiero-cambio/",
			headers=self.user._auth_headers(),
			name="/api/partida/[id]/mano/quiero-cambio/",
		)

	@task(1)
	def jugador_no_quiere_cambiar(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.put(
			f"/api/partida/{partida_id}/mano/no-quiero-cambio/",
			headers=self.user._auth_headers(),
			name="/api/partida/[id]/mano/no-quiero-cambio/",
		)

	@task(1)
	def cambiar_cartas(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.put(
			f"/api/partida/{partida_id}/mano/cambiar-cartas/",
			json={"cartas": ["2_OROS"]},
			headers=self.user._auth_headers(),
			name="/api/partida/[id]/mano/cambiar-cartas/",
		)

	@task(1)
	def elegir_carta_comodin(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.put(
			f"/api/partida/{partida_id}/mano/elegir-carta-comodin/",
			json={"carta_comodin": "MONEDERO_PECULIAR"},
			headers=self.user._auth_headers(),
			name="/api/partida/[id]/mano/elegir-carta-comodin/",
		)

	@task(1)
	def siguiente_mano(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		self.client.post(
			f"/api/partida/{partida_id}/mano/siguiente-mano/",
			headers=self.user._auth_headers(),
			name="/api/partida/[id]/mano/siguiente-mano/",
		)


class ManoLoad(AuthenticatedApiUser):
	tasks = [ManoTaskSet]
