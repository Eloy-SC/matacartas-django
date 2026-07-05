import os
from uuid import uuid4

from locust import HttpUser, between
from locust.exception import StopUser


def build_csrf_headers(csrf_token):
	return {"X-CSRFToken": csrf_token, "Referer": "/"}


def unique_suffix() -> str:
	return uuid4().hex[:8]


class AuthenticatedApiUser(HttpUser):
	wait_time = between(1, 3)

	username = os.getenv("LOCUST_USERNAME", "cervantes")
	password = os.getenv("LOCUST_PASSWORD", "123456")
	csrf_token = None
	user_id = None

	def on_start(self):
		self._authenticate()

	def _fetch_csrf_token(self):
		response = self.client.get("/api/auth/csrf/", name="/api/auth/csrf/")
		if response.status_code != 200:
			raise StopUser(f"No se pudo obtener CSRF: {response.status_code}")

		token = response.json().get("csrfToken")
		if not token:
			raise StopUser("No se recibió csrfToken")

		return token

	def _authenticate(self):
		initial_csrf = self._fetch_csrf_token()
		login_response = self.client.post(
			"/api/auth/login/",
			json={"username": self.username, "password": self.password},
			headers=build_csrf_headers(initial_csrf),
			name="/api/auth/login/",
		)
		if login_response.status_code != 200:
			raise StopUser(
				f"No se pudo iniciar sesión como {self.username}: {login_response.status_code}"
			)

		self.user_id = login_response.json().get("id")
		self.csrf_token = self._fetch_csrf_token()

	def _auth_headers(self):
		if not self.csrf_token:
			raise StopUser("No hay CSRF disponible para peticiones autenticadas")
		return build_csrf_headers(self.csrf_token)