from itertools import count

from locust import HttpUser, between, task


API_PREFIX = "/api"
HOST = "http://localhost:8000"
PARTIDA_IDS = {
    1: 30,
    2: 31,
    3: 32,
    4: 33,
    5: 34,
}

# Contador para asignar automáticamente los usuarios
# locust_player_1 ... locust_player_10
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

        # Dos jugadores por partida
        numero_partida = ((self.player_number - 1) // 2) + 1
        self.partida_id = PARTIDA_IDS[numero_partida]

        self.username = f"locust_player_{self.player_number}"
        self.password = f"locust_password_{self.player_number}"

        # El jugador impar es ROJO y el par AZUL
        self.es_rojo = self.player_number % 2 == 1

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

        self.carta = "1_OROS"
        self.accion_realizada = False

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
    def jugar_o_retirarse(self):

        # ROJO juega directamente porque sabemos que
        # todas las partidas empiezan con ROJO.
        if self.es_rojo and not self.accion_realizada:
            self.jugar_carta()

        # AZUL comprueba primero si ya es su turno.
        elif not self.es_rojo and not self.accion_realizada:
            self.comprobar_turno_y_retirarse()


    def comprobar_turno_y_retirarse(self):
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

        turno_actual = datos["partida"]["turno_actual"]

        if turno_actual != "azul":
            return

        self.retirarse()


    def jugar_carta(self):
        csrf_token = self.client.cookies.get("csrftoken")

        response = self.client.put(
            f"{API_PREFIX}/partida/"
            f"{self.partida_id}/mano/ronda/jugar-carta/",
            json={
                "carta": self.carta,
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

        self.accion_realizada = True

        print(
            f"{self.username} ha jugado "
            f"{self.carta} en partida "
            f"{self.partida_id}"
        )


    def retirarse(self):
        csrf_token = self.client.cookies.get("csrftoken")

        response = self.client.put(
            f"{API_PREFIX}/partida/"
            f"{self.partida_id}/mano/ronda/retirarse/",
            headers={
                "X-CSRFToken": csrf_token,
            },
        )

        if response.status_code not in (200, 201):
            print(
                f"RETIRARSE {self.username} -> "
                f"{response.status_code} "
                f"{response.text}"
            )
            return

        self.accion_realizada = True

        print(
            f"{self.username} se ha retirado "
            f"de partida "
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