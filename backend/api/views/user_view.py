from api.utils.exceptions import ActualizarPerfilError, RegistrationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..serializers.user_serializer import (
    AdminUserUpdateSerializer,
    PerfilUpdateSerializer,
    UserSerializer,
)
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
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1
    page_size = 10

    try:
        paged = user_service.listar_usuarios_admin(
            request.user,
            page=page,
            page_size=page_size,
        )
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
        for usuario in paged["items"]
    ]

    return Response(
        {
            "items": data,
            "page": paged["page"],
            "page_size": paged["page_size"],
            "total": paged["total"],
            "total_pages": paged["total_pages"],
        },
        status=200,
    )

@api_view(["GET"])
@permission_classes([])
def get_usuario_admin(request, user_id):
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

@api_view(["PUT"])
@permission_classes([])
def editar_usuario_admin(request, user_id):
    UserModel = get_user_model()
    target_user = UserModel.objects.filter(id=user_id).first()
    if target_user is None:
        return Response({"detail": "Usuario no encontrado"}, status=404)

    serializer = AdminUserUpdateSerializer(
        data=request.data,
        context={"user": target_user},
    )

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
            "id": usuario.id,
            "username": usuario.get_username(),
            "detail": "Usuario actualizado",
        },
        status=status.HTTP_200_OK,
    )

@api_view(["DELETE"])
@permission_classes([])
def eliminar_usuario_admin(request, user_id):
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
            "id": usuario.id,
            "username": usuario.get_username(),
            "detail": "Usuario creado",
        },
        status=status.HTTP_201_CREATED,
    )

