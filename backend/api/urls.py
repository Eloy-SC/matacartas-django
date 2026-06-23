from django.urls import path

from .views.partida_view import (
    abandonar_partida,
    crear_partida,
    editar_partida,
    expulsar_jugador,
    get_jugador_participa_en_partida,
    get_jugador_participa_en_partida_privada,
    get_jugadores_partida,
    get_partida_como_jugador,
    iniciar_partida,
    listar_partidas_publicas,
    toggle_listo,
    unirse_a_partida_privada,
    unirse_a_partida_publica
)

from .views.auth_view import csrf, me, register, session_login, session_logout
from .views.user_view import (
    crear_usuario_admin,
    editar_usuario_admin,
    eliminar_usuario_admin,
    get_usuario_admin,
    listar_top_usuarios,
    listar_usuarios_admin,
    perfil_actualizar,
)
from .views.rango_view import (
    crear_rango_admin,
    editar_rango_admin,
    eliminar_rango_admin,
    get_rango,
    get_rango_de_usuario,
    listar_rangos,
)
from .views.health_view import health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("auth/csrf/", csrf, name="csrf"),
    path("auth/login/", session_login, name="session-login"),
    path("auth/register/", register, name="register"),
    path("auth/logout/", session_logout, name="session-logout"),
    path("auth/me/", me, name="me"),
    path("users/perfil/actualizar/", perfil_actualizar, name="perfil-actualizar"),
    path("users/admin/listar/", listar_usuarios_admin, name="listar-usuarios-admin"),
    path("users/admin/crear/", crear_usuario_admin, name="crear-usuario-admin"),
    path("users/admin/<int:user_id>/", get_usuario_admin, name="get-usuario-admin"),
    path(
        "users/admin/<int:user_id>/editar/",
        editar_usuario_admin,
        name="editar-usuario-admin",
    ),
    path(
        "users/admin/<int:user_id>/eliminar/",
        eliminar_usuario_admin,
        name="eliminar-usuario-admin",
    ),
    path("users/top/", listar_top_usuarios, name="listar-top-usuarios"),
    path("rangos/listar/", listar_rangos, name="listar-rangos"),
    path("rangos/admin/crear/", crear_rango_admin, name="crear-rango-admin"),
    path("rangos/<int:rango_id>/", get_rango, name="get-rango"),
    path("rangos/usuario/<int:user_id>/", get_rango_de_usuario, name="get-rango-de-usuario"),
    path(
        "rangos/admin/<int:rango_id>/editar/",
        editar_rango_admin,
        name="editar-rango-admin",
    ),
    path(
        "rangos/admin/<int:rango_id>/eliminar/",
        eliminar_rango_admin,
        name="eliminar-rango-admin",
    ),
    path("partidas/publicas/", listar_partidas_publicas, name="listar-partidas-publicas"),
    path("partidas/crear/", crear_partida, name="crear-partida"),
    path("partidas/<int:partida_id>/editar/", editar_partida, name="editar-partida"),
    path("partidas/<int:partida_id>/jugador/", get_partida_como_jugador, name="get-partida-como-jugador"),
    path("partidas/<int:partida_id>/jugadores/", get_jugadores_partida, name="get-jugadores-partida"),
    path("partidas/<int:partida_id>/participa/", get_jugador_participa_en_partida, name="get-jugador-participa-en-partida"),
    path("partidas/<str:clave>/participa/", get_jugador_participa_en_partida_privada, name="get-jugador-participa-en-partida-privada"),
    path("partidas/<int:partida_id>/abandonar/", abandonar_partida, name="abandonar-partida"),
    path("partidas/<int:partida_id>/unirse/", unirse_a_partida_publica, name="unirse-a-partida-publica"),
    path("partidas/<str:clave>/unirse/", unirse_a_partida_privada, name="unirse-a-partida-privada"),
    path("partidas/<int:partida_id>/toggle-listo/", toggle_listo, name="toggle-listo"),
    path("partidas/<int:partida_id>/expulsar-jugador/<int:jugador_id>/", expulsar_jugador, name="expulsar-jugador"),
    path("partidas/<int:partida_id>/iniciar/", iniciar_partida, name="iniciar-partida")
]
