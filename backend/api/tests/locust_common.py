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
	# Mark as abstract so Locust won't try to instantiate this base user directly
	abstract = True

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
		# If auto-register is enabled and this is not an admin user, create a fresh user first
		auto_register_disabled = os.getenv("LOCUST_NO_AUTO_REGISTER", "0") == "1"
		is_admin_user = self.username == "admin" or self.username == os.getenv("LOCUST_ADMIN_USERNAME")
		if not auto_register_disabled and not is_admin_user:
			# register unique user and then login to avoid initial failed login attempts
			suffix = unique_suffix()
			new_username = f"{self.username}_{suffix}"
			register_payload = {
				"username": new_username,
				"password": self.password,
				"email": f"{new_username}@example.com",
				"nombre": new_username,
			}
			reg_resp = self.client.post(
				"/api/auth/register/",
				json=register_payload,
				headers=build_csrf_headers(initial_csrf),
				name="/api/auth/register/",
			)
			if reg_resp.status_code != 201:
				raise StopUser(f"Registro automatico falló: {reg_resp.status_code}")
			self.username = new_username
			login_response = self.client.post(
				"/api/auth/login/",
				json={"username": self.username, "password": self.password},
				headers=build_csrf_headers(initial_csrf),
				name="/api/auth/login/",
			)
			if login_response.status_code != 200:
				raise StopUser(f"No se pudo iniciar sesión después de registrar: {login_response.status_code}")
		else:
			# try login-first for admin users or when auto-register disabled
			login_response = self.client.post(
				"/api/auth/login/",
				json={"username": self.username, "password": self.password},
				headers=build_csrf_headers(initial_csrf),
				name="/api/auth/login/",
			)
			# If admin login fails, try fallback to the default locust user
			if login_response.status_code != 200 and (self.username == "admin"):
				fallback = os.getenv("LOCUST_USERNAME", "cervantes")
				if fallback and fallback != "admin":
					self.username = fallback
					login_response = self.client.post(
						"/api/auth/login/",
						json={"username": self.username, "password": self.password},
						headers=build_csrf_headers(initial_csrf),
						name="/api/auth/login/",
					)
					# if still failing, fall through to registration attempt or stop
			# If auto-register is disabled and login failed, stop
			if auto_register_disabled and login_response.status_code != 200:
				raise StopUser(f"No se pudo iniciar sesión como {self.username}: {login_response.status_code}")

		self.user_id = login_response.json().get("id")
		self.csrf_token = self._fetch_csrf_token()

	def _auth_headers(self):
		if not self.csrf_token:
			raise StopUser("No hay CSRF disponible para peticiones autenticadas")
		return build_csrf_headers(self.csrf_token)