from django.urls import path
from .views.auth_view import csrf, me, register, session_login, session_logout
from .views.user_view import (
    crear_usuario_admin,
    get_usuario_admin,
    listar_usuarios_admin,
    perfil_actualizar,
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
]
