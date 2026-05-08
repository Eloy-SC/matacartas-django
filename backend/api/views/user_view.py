from api.utils.exceptions import ActualizarPerfilError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
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

