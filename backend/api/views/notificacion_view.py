from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..services import notificacion_service

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_notificaciones(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    try:
        paged = notificacion_service.listar_notificaciones(
            request.user,
            page=page,
            page_size=10
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    return Response(paged, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enviar_solicitud_amistad(request, objetivo_id):

    try:
        notificacion_service.enviar_solicitud_amistad(request.user, objetivo_id)
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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enviar_invitacion_partida(request, objetivo_id, partida_id):

    try:
        notificacion_service.enviar_invitacion_partida(request.user, objetivo_id, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def aceptar_invitacion_partida(request, invitacion_id):
    try:
        notificacion_service.contestar_invitacion_partida(request.user, invitacion_id, aceptar=True)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def rechazar_invitacion_partida(request, invitacion_id):
    try:
        notificacion_service.contestar_invitacion_partida(request.user, invitacion_id, aceptar=False)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)