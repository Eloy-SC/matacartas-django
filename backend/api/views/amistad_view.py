from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..services import amistad_service

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_usuarios_busqueda_amistad(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    try:
        paged = amistad_service.listar_usuarios_busqueda_amistad(
            request.user,
            page=page,
            page_size=5,
            search=(request.query_params.get("search") or "").strip() or None,
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    return Response(paged, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_amigos(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    try:
        paged = amistad_service.listar_amigos_paginated(
            request.user,
            page=page,
            page_size=5,
            search=(request.query_params.get("search") or "").strip() or None,
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    return Response(paged, status=status.HTTP_200_OK)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def eliminar_amigo(request, amigo_id):
    try:
        amistad_service.eliminar_amigo(request.user, amigo_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)