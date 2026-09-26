from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..services import notificacion_service

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enviar_solicitud_amistad(request, receptor_id):

    try:
        notificacion_service.enviar_solicitud_amistad(request.user, receptor_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def aceptar_solicitud_amistad(request, solicitud_id):
    try:
        notificacion_service.contestar_solicitud_amistad(request.user, solicitud_id, aceptar=True)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def rechazar_solicitud_amistad(request, solicitud_id):
    try:
        notificacion_service.contestar_solicitud_amistad(request.user, solicitud_id, aceptar=False)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)