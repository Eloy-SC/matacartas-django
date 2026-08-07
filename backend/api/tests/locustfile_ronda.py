from locust import SequentialTaskSet, task

from api.tests.locust_common import AuthenticatedApiUser


def _first_partida_id(response):
	items = response.json().get("items", [])
	if not items:
		return None
	return items[0].get("id")


class RondaTaskSet(SequentialTaskSet):
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
	def jugar_carta(self):
		partida_id = self._ensure_joined_partida()
		if not partida_id:
			return

		mesa_response = self.client.get(
			f"/api/partida/{partida_id}/mano/mesa/",
			name="/api/partida/[id]/mano/mesa/",
		)
		carta = "2_OROS"
		if mesa_response.status_code == 200:
			jugador = mesa_response.json().get("jugador") or {}
			cartas = jugador.get("cartas") or []
			if cartas:
				carta = cartas[0]

		self.client.put(
			f"/api/partida/{partida_id}/mano/ronda/jugar-carta/",
			json={"carta": carta},
			headers=self.user._auth_headers(),
			name="/api/partida/[id]/mano/ronda/jugar-carta/",
		)


class RondaLoad(AuthenticatedApiUser):
	tasks = [RondaTaskSet]
