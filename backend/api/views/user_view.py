from api.utils.exceptions import ActualizarPerfilError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers.user_serializer import PerfilUpdateSerializer
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
            "id": usuario.id,
            "username": usuario.get_username(),
            "email": usuario.email,
            "is_staff": usuario.is_staff,
            "is_active": usuario.is_active,
        }
        for usuario in usuarios
    ]

    return Response(data, status=200)

