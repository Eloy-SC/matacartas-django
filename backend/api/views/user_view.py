from api.utils.exceptions import ActualizarPerfilError, RegistrationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers.user_serializer import PerfilUpdateSerializer, UserSerializer
from ..services import user_service

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def perfil_actualizar(request):
    serializer = PerfilUpdateSerializer(data=request.data, context={"user": request.user})

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    try:
        usuario = user_service.actualizar_perfil(request.user, **serializer.validated_data)
    except ActualizarPerfilError as e:
        return Response(e.errors, status=400)
    
    return Response(
        {
            "id": usuario.id,
            "username": usuario.get_username(),
            "detail": "Perfil actualizado",
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
@permission_classes([])
def listar_usuarios_admin(request):
    try:
        usuarios = user_service.listar_usuarios_admin(request.user)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    data = [
        {
            "id": usuario["id"],
            "username": usuario["username"],
            "email": usuario["email"],
            "nombre": usuario["nombre"],
            "puntuacion": usuario["puntuacion"],
            "imagen": usuario["imagen"],
            "is_staff": usuario["is_staff"],
            "is_active": usuario["is_active"],
        }
        for usuario in usuarios
    ]

    return Response(data, status=200)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([])
def get_usuario_admin(request, user_id):
    if request.method == "GET":
        try:
            usuario = user_service.get_usuario_admin(request.user, user_id)
        except PermissionError as e:
            return Response({"detail": str(e)}, status=403)

        if not usuario:
            return Response({"detail": "Usuario no encontrado"}, status=404)

        data = {
            "id": usuario["id"],
            "username": usuario["username"],
            "email": usuario["email"],
            "nombre": usuario["nombre"],
            "puntuacion": usuario["puntuacion"],
            "imagen": usuario["imagen"],
            "is_staff": usuario["is_staff"],
            "is_active": usuario["is_active"],
        }

        return Response(data, status=200)

    if request.method == "PUT":
        serializer = UserSerializer(data=request.data, context={"user": request.user})

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            usuario = user_service.editar_usuario_admin(
                request.user, user_id, **serializer.validated_data
            )
        except RegistrationError as e:
            return Response(e.errors, status=400)
        except ValueError as e:
            return Response({"detail": str(e)}, status=404)

        return Response(
            {
                "id": usuario["id"],
                "username": usuario["username"],
                "detail": "Usuario actualizado",
            },
            status=status.HTTP_200_OK,
        )

    try:
        user_service.eliminar_usuario_admin(request.user, user_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response({"detail": "Usuario eliminado"}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([])
def crear_usuario_admin(request):
    serializer = UserSerializer(data=request.data, context={"user": request.user})

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    try:
        usuario = user_service.crear_usuario_admin(request.user, **serializer.validated_data)
    except RegistrationError as e:
        return Response(e.errors, status=400)
    
    return Response(
        {
            "id": usuario["id"],
            "username": usuario["username"],
            "detail": "Usuario creado",
        },
        status=status.HTTP_201_CREATED,
    )

