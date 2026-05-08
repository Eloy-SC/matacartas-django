from django.urls import path
from .views.auth_view import csrf, me, register, session_login, session_logout
from .views.user_view import perfil_actualizar
from .views.health_view import health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("auth/csrf/", csrf, name="csrf"),
    path("auth/login/", session_login, name="session-login"),
    path("auth/register/", register, name="register"),
    path("auth/logout/", session_logout, name="session-logout"),
    path("auth/me/", me, name="me"),
    path("users/perfil/actualizar/", perfil_actualizar, name="perfil-actualizar"),
]
