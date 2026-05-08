from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from ..utils.exceptions import RegistrationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from ..serializers.user_serializer import UserSerializer
from ..services import auth_service


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf(request):
    """Ensure the CSRF cookie is set and return the token.

    The frontend should call this once before making any POST/PUT/PATCH/DELETE
    requests that rely on SessionAuthentication.
    """

    return Response({"csrfToken": get_token(request)})


@api_view(["POST"])
@permission_classes([AllowAny])
def session_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Falta el nombre de usuario o la contraseña"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Credenciales inválidas"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    login(request, user)
    return Response(
        {
            "id": user.id,
            "username": user.get_username(),
            "isAuthenticated": True,
        }
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def session_logout(request):
    logout(request)
    return Response({"detail": "Sesión cerrada"})

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        usuario = auth_service.registrar_usuario(**serializer.validated_data)
    except RegistrationError as e:
        return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "id": usuario.id,
            "username": usuario.get_username(),
            "detail": "Usuario creado",
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    try:
        user_perfil = auth_service.me(request.user)
    except Exception:
        return Response(
            {"detail": "No se pudo obtener el usuario autenticado"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    user = user_perfil[0]
    perfil = user_perfil[1]
    
    return Response(
        {
            "id": user.id,
            "username": getattr(user, "username", ""),
            "email": getattr(user, "email", ""),
            "isAuthenticated": True,
            "perfil": {
                "nombre": getattr(perfil, "nombre", None),
                "puntuacion": getattr(perfil, "puntuacion", None),
                "imagen": getattr(perfil, "imagen", None),
            },
        }
    )
