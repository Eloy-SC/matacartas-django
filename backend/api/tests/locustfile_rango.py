from locust import SequentialTaskSet, task

from api.tests.locust_common import AuthenticatedApiUser, unique_suffix


class RangosLecturaTaskSet(SequentialTaskSet):
	rangos_ids = []

	def on_start(self):
		self.rangos_ids = []

	def _get_rangos(self):
		response = self.client.get("/api/rangos/listar/", name="/api/rangos/listar/")
		if response.status_code != 200:
			return []

		self.rangos_ids = [item["id"] for item in response.json() if item.get("id")]
		return self.rangos_ids

	@task(4)
	def listar_rangos(self):
		self._get_rangos()

	@task(2)
	def get_rango(self):
		rangos_ids = self._get_rangos()
		if not rangos_ids:
			return

		self.client.get(
			f"/api/rangos/{rangos_ids[0]}/",
			name="/api/rangos/[id]/",
		)

	@task(2)
	def get_rango_de_usuario(self):
		if not self.user.user_id:
			return

		self.client.get(
			f"/api/rangos/usuario/{self.user.user_id}/",
			name="/api/rangos/usuario/[id]/",
		)


class RangosAdminTaskSet(SequentialTaskSet):
	created_rango_id = None
	created_rango_nombre = None

	def on_start(self):
		self.created_rango_id = None
		self.created_rango_nombre = None

	def _create_payload(self):
		suffix = unique_suffix()
		return {
			"nombre": f"LocustRango{suffix}",
			"color": "morado_claro",
			"puntos_minimos": 9000000,
			"puntos_maximos": 9000005,
		}

	@task(2)
	def crear_rango_admin(self):
		if self.created_rango_id:
			return

		payload = self._create_payload()
		response = self.client.post(
			"/api/rangos/admin/crear/",
			json=payload,
			headers=self.user._auth_headers(),
			name="/api/rangos/admin/crear/",
		)
		if response.status_code != 201:
			return

		self.created_rango_id = response.json().get("id")
		self.created_rango_nombre = payload["nombre"]

	@task(2)
	def editar_rango_admin(self):
		if not self.created_rango_id:
			return

		suffix = unique_suffix()
		payload = {
			"nombre": f"{self.created_rango_nombre}_{suffix}",
			"color": "azul_cian",
			"puntos_minimos": 9000010,
			"puntos_maximos": 9000015,
		}
		response = self.client.put(
			f"/api/rangos/admin/{self.created_rango_id}/editar/",
			json=payload,
			headers=self.user._auth_headers(),
			name="/api/rangos/admin/[id]/editar/",
		)
		if response.status_code == 200:
			self.created_rango_nombre = payload["nombre"]

	@task(2)
	def eliminar_rango_admin(self):
		if not self.created_rango_id:
			return

		response = self.client.delete(
			f"/api/rangos/admin/{self.created_rango_id}/eliminar/",
			headers=self.user._auth_headers(),
			name="/api/rangos/admin/[id]/eliminar/",
		)
		if response.status_code == 200:
			self.created_rango_id = None
			self.created_rango_nombre = None


class RangoPublicoLoad(AuthenticatedApiUser):
	tasks = [RangosLecturaTaskSet]


class RangoAdminLoad(AuthenticatedApiUser):
	username = "admin"
	password = "123456"
	tasks = [RangosAdminTaskSet, RangosLecturaTaskSet]