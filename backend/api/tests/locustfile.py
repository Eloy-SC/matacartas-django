from itertools import count

from locust import HttpUser, between, task


API_PREFIX = "/api"
HOST = "http://localhost:8000"
PARTIDA_IDS = {
    # Sustituir estos valores por los IDs que imprime preparar_locust.
    1: 18,
    2: 19,
    3: 20,
    4: 21,
    5: 22,
    6: 23,
    7: 24,
    8: 25,
}

# Contador para asignar automáticamente los usuarios
# locust_player_1 ... locust_player_32
_player_counter = count(1)


class UsuarioLectura(HttpUser):
    host = HOST
    wait_time = between(1, 3)

    def obtener_csrf(self):
        response = self.client.get(
            f"{API_PREFIX}/auth/csrf"
        )

        if response.status_code != 200:
            print(
                f"CSRF -> {response.status_code} "
                f"{response.text}"
            )

    def on_start(self):
        self.obtener_csrf()

        csrf_token = self.client.cookies.get("csrftoken")

        response = self.client.post(
            f"{API_PREFIX}/auth/login/",
            json={
                "username": "locust_user",
                "password": "locust_password",
            },
            headers={
                "X-CSRFToken": csrf_token,
            },
        )

        if response.status_code != 200:
            print(
                f"LOGIN -> {response.status_code} "
                f"{response.text}"
            )

    @task(5)
    def partidas_publicas(self):
        self.client.get(
            f"{API_PREFIX}/partidas/publicas/"
        )

    @task(3)
    def top_usuarios(self):
        self.client.get(
            f"{API_PREFIX}/users/top/"
        )

    @task(2)
    def rangos(self):
        self.client.get(
            f"{API_PREFIX}/rangos/listar/"
        )


class UsuarioPartida(HttpUser):
    host = HOST
    wait_time = between(1, 3)

    def obtener_csrf(self):
        response = self.client.get(
            f"{API_PREFIX}/auth/csrf"
        )

        if response.status_code != 200:
            print(
                f"CSRF -> {response.status_code} "
                f"{response.text}"
            )

    def on_start(self):
        self.player_number = next(_player_counter)

        # Cuatro jugadores por partida y ocho partidas en total.
        numero_partida = ((self.player_number - 1) // 4) + 1
        self.partida_id = PARTIDA_IDS[numero_partida]

        if self.partida_id is None:
            raise RuntimeError(
                "Debes copiar en PARTIDA_IDS los IDs que imprime preparar_locust."
            )

        self.username = f"locust_player_{self.player_number}"
        self.password = f"locust_password_{self.player_number}"

        self.obtener_csrf()

        csrf_token = self.client.cookies.get("csrftoken")

        response = self.client.post(
            f"{API_PREFIX}/auth/login/",
            json={
                "username": self.username,
                "password": self.password,
            },
            headers={
                "X-CSRFToken": csrf_token,
            },
        )

        print(
            f"LOGIN {self.username}: "
            f"{response.status_code} - {response.text}"
        )

        print(
            f"COOKIES {self.username}: "
            f"{self.client.cookies}"
        )

        if response.status_code != 200:
            print(
                f"LOGIN {self.username} -> "
                f"{response.status_code} "
                f"{response.text}"
            )

    @task(5)
    def mesa(self):
        self.client.get(
            f"{API_PREFIX}/partida/"
            f"{self.partida_id}/mano/mesa/"
        )

    @task(3)
    def jugadores(self):
        self.client.get(
            f"{API_PREFIX}/partidas/"
            f"{self.partida_id}/jugadores/"
        )

    @task(2)
    def partida(self):
        self.client.get(
            f"{API_PREFIX}/partidas/"
            f"{self.partida_id}/jugador/"
        )

    @task(2)
    def participacion(self):
        self.client.get(
            f"{API_PREFIX}/partidas/"
            f"{self.partida_id}/participa/"
        )

    @task
    def actuar_en_partida(self):
        response = self.client.get(
            f"{API_PREFIX}/partida/"
            f"{self.partida_id}/mano/mesa/"
        )

        if response.status_code != 200:
            print(
                f"MESA {self.username} -> "
                f"{response.status_code} "
                f"{response.text}"
            )
            return

        datos = response.json()
        partida = datos.get("partida", {})
        jugador = datos.get("jugador", {})
        rondas = datos.get("rondas", [])
        ronda_actual = rondas[-1] if rondas else None

        if not ronda_actual or partida.get("turno_actual") != jugador.get("color"):
            return

        ronda_num = ronda_actual.get("ronda_num")
        cambios = ronda_actual.get("cambios")

        if ronda_num == 0 and cambios == 0:
            self.no_quiero_cambio()
        elif ronda_num in (1, 2, 3):
            cartas = jugador.get("cartas") or []
            if cartas:
                self.jugar_carta(cartas[0])


    def no_quiero_cambio(self):
        csrf_token = self.client.cookies.get("csrftoken")

        response = self.client.put(
            f"{API_PREFIX}/partida/"
            f"{self.partida_id}/mano/no-quiero-cambio/",
            headers={"X-CSRFToken": csrf_token},
        )

        if response.status_code not in (200, 201):
            print(
                f"NO QUIERO CAMBIO {self.username} -> "
                f"{response.status_code} {response.text}"
            )


    def jugar_carta(self, carta):
        csrf_token = self.client.cookies.get("csrftoken")

        response = self.client.put(
            f"{API_PREFIX}/partida/"
            f"{self.partida_id}/mano/ronda/jugar-carta/",
            json={
                "carta": carta,
            },
            headers={
                "X-CSRFToken": csrf_token,
            },
        )

        if response.status_code not in (200, 201):
            print(
                f"JUGAR CARTA {self.username} -> "
                f"{response.status_code} "
                f"{response.text}"
            )
            return

        print(
            f"{self.username} ha jugado "
            f"{carta} en partida "
            f"{self.partida_id}"
        )


class Administrador(HttpUser):
    host = HOST
    wait_time = between(2, 5)

    def obtener_csrf(self):
        response = self.client.get(
            f"{API_PREFIX}/auth/csrf"
        )

        if response.status_code != 200:
            print(
                f"CSRF -> {response.status_code} "
                f"{response.text}"
            )

    def on_start(self):
        self.obtener_csrf()

        csrf_token = self.client.cookies.get("csrftoken")

        response = self.client.post(
            f"{API_PREFIX}/auth/login/",
            json={
                "username": "locust_user",
                "password": "locust_password",
            },
            headers={
                "X-CSRFToken": csrf_token,
            },
        )

        if response.status_code != 200:
            print(
                f"LOGIN ADMIN -> {response.status_code} "
                f"{response.text}"
            )

    @task(5)
    def listar_usuarios(self):
        self.client.get(
            f"{API_PREFIX}/users/admin/listar/"
        )

    @task(3)
    def listar_rangos(self):
        self.client.get(
            f"{API_PREFIX}/rangos/listar/"
        )

    @task(2)
    def listar_logros(self):
        self.client.get(
            f"{API_PREFIX}/logros/admin/listar/"
        )

    @task(2)
    def listar_medallas(self):
        self.client.get(
            f"{API_PREFIX}/medallas/listar/"
        )

    @task(2)
    def listar_amigos(self):
        self.client.get(
            f"{API_PREFIX}/amigos/listar/"
        )

    @task(2)
    def listar_notificaciones(self):
        self.client.get(
            f"{API_PREFIX}/notificaciones/listar/"
        )

    @task(2)
    def listar_anuncios(self):
        self.client.get(
            f"{API_PREFIX}/anuncios/admin/listar/"
        )

    @task(2)
    def obtener_estadisticas_globales(self):
        self.client.get(
            f"{API_PREFIX}/estadisticas/globales/"
        )

    @task(2)
    def obtener_estadisticas_individuales(self):
        self.client.get(
            f"{API_PREFIX}/estadisticas/individuales/"
        )