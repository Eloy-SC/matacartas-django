from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


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
            {"detail": "Missing username or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Invalid credentials"},
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
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Missing username or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"detail": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, password=password)
    return Response(
        {
            "id": user.id,
            "username": user.get_username(),
            "detail": "User created",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def session_logout(request):
    logout(request)
    return Response({"detail": "Logged out"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.get_username(),
            "isAuthenticated": True,
        }
    )
