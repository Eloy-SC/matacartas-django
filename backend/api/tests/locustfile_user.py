import os

from locust import SequentialTaskSet, task

from api.tests.locust_common import AuthenticatedApiUser, unique_suffix


class PerfilYTopUsuariosTaskSet(SequentialTaskSet):
	@task(3)
	def listar_top_usuarios(self):
		self.client.get("/api/users/top/", name="/api/users/top/")

	@task(1)
	def actualizar_perfil(self):
		suffix = unique_suffix()
		payload = {
			"username": f"{self.user.username}_{suffix}",
			"email": f"{self.user.username}_{suffix}@example.com",
			"nombre": f"{getattr(self.user, 'nombre', self.user.username)} {suffix}",
			"imagen": "",
		}

		self.client.put(
			"/api/users/perfil/actualizar/",
			json=payload,
			headers=self.user._auth_headers(),
			name="/api/users/perfil/actualizar/",
		)


class AdminUsuariosTaskSet(SequentialTaskSet):
	created_user_id = None
	listed_user_ids = []

	def on_start(self):
		self.listed_user_ids = []

	@task(4)
	def listar_usuarios_admin(self):
		response = self.client.get(
			"/api/users/admin/listar/",
			params={"page": 1, "ordering": "-puntuacion"},
			name="/api/users/admin/listar/",
		)

		if response.status_code != 200:
			return

		self.listed_user_ids = [
			item["id"] for item in response.json().get("items", []) if item.get("id")
		]

	@task(2)
	def get_usuario_admin(self):
		if not self.listed_user_ids:
			self.listar_usuarios_admin()

		target_user_id = next(
			(user_id for user_id in self.listed_user_ids if user_id != self.user.user_id),
			None,
		)
		if target_user_id is None:
			return

		self.client.get(
			f"/api/users/admin/{target_user_id}/",
			name="/api/users/admin/[id]/",
		)

	@task(1)
	def crear_editar_eliminar_usuario_admin(self):
		suffix = unique_suffix()
		base_username = f"locust_{suffix}"
		create_payload = {
			"username": base_username,
			"password": f"Pass-{suffix}-123",
			"email": f"{base_username}@example.com",
			"nombre": f"Usuario Locust {suffix}",
			"imagen": "",
			"is_staff": False,
		}

		create_response = self.client.post(
			"/api/users/admin/crear/",
			json=create_payload,
			headers=self.user._auth_headers(),
			name="/api/users/admin/crear/",
		)

		if create_response.status_code != 201:
			return

		self.created_user_id = create_response.json().get("id")
		if not self.created_user_id:
			return

		edit_payload = {
			"username": f"{base_username}_edit",
			"password": f"Pass-{suffix}-456",
			"email": f"{base_username}_edit@example.com",
			"nombre": f"Usuario Locust Editado {suffix}",
			"imagen": "",
			"is_staff": False,
		}

		self.client.put(
			f"/api/users/admin/{self.created_user_id}/editar/",
			json=edit_payload,
			headers=self.user._auth_headers(),
			name="/api/users/admin/[id]/editar/",
		)

		self.client.delete(
			f"/api/users/admin/{self.created_user_id}/eliminar/",
			headers=self.user._auth_headers(),
			name="/api/users/admin/[id]/eliminar/",
		)


class NormalUserLoad(AuthenticatedApiUser):
	tasks = [PerfilYTopUsuariosTaskSet]


class AdminUserLoad(AuthenticatedApiUser):
	username = os.getenv("LOCUST_ADMIN_USERNAME", "admin")
	password = os.getenv("LOCUST_ADMIN_PASSWORD", "123456")
	tasks = [AdminUsuariosTaskSet, PerfilYTopUsuariosTaskSet]