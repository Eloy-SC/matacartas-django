from ..serializers.anuncio_serializer import AnuncioSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..services import anuncio_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_anuncios_admin(request):
    try:
        anuncios = anuncio_service.listar_anuncios_admin(request.user)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    data = [
        {
            "id": anuncio["id"],
            "titulo": anuncio["titulo"],
            "fecha_ult_mod": anuncio["fecha_ult_mod"],
            "fecha_publicacion": anuncio["fecha_publicacion"],
            "autor": anuncio["autor"].username,
        }
        for anuncio in anuncios
    ]

    return Response(data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_anuncios_publicos(request):
    try:
        anuncios = anuncio_service.listar_anuncios_publicos(request.user)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    data = [
        {
            "id": anuncio["id"],
            "titulo": anuncio["titulo"],
            "subtitulo": anuncio["subtitulo"],
            "fecha_publicacion": anuncio["fecha_publicacion"],
            "autor": anuncio["autor"].username,
        }
        for anuncio in anuncios
    ]

    return Response(data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_anuncio(request, anuncio_id):
    try:
        anuncio = anuncio_service.get_anuncio(request.user, anuncio_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    if not anuncio:
        return Response({"detail": "Anuncio no encontrado"}, status=404)

    data = {
        "id": anuncio.id,
        "titulo": anuncio.titulo,
        "subtitulo": anuncio.subtitulo,
        "descripcion": anuncio.descripcion,
        "fecha_ult_mod": anuncio.fecha_ult_mod,
        "fecha_publicacion": anuncio.fecha_publicacion,
        "autor": anuncio.autor.username,
    }

    return Response(data, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_anuncio_admin(request):
    serializer = AnuncioSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        anuncio = anuncio_service.crear_anuncio_admin(request.user, **serializer.validated_data)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    data = {
        "id": anuncio.id,
        "titulo": anuncio.titulo,
        "subtitulo": anuncio.subtitulo,
        "descripcion": anuncio.descripcion,
        "fecha_ult_mod": anuncio.fecha_ult_mod,
        "fecha_publicacion": anuncio.fecha_publicacion,
        "autor": anuncio.autor.username,
    }

    return Response(data, status=201)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def editar_anuncio_admin(request, anuncio_id):
    serializer = AnuncioSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        anuncio = anuncio_service.editar_anuncio_admin(
            request.user, anuncio_id, **serializer.validated_data
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    data = {
        "id": anuncio.id,
        "titulo": anuncio.titulo,
        "subtitulo": anuncio.subtitulo,
        "descripcion": anuncio.descripcion,
        "fecha_ult_mod": anuncio.fecha_ult_mod,
        "fecha_publicacion": anuncio.fecha_publicacion,
        "autor": anuncio.autor.username,
    }

    return Response(data, status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def publicar_anuncio_admin(request, anuncio_id):
    try:
        anuncio = anuncio_service.publicar_anuncio_admin(request.user, anuncio_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    data = {
        "id": anuncio.id,
        "titulo": anuncio.titulo,
        "subtitulo": anuncio.subtitulo,
        "descripcion": anuncio.descripcion,
        "fecha_ult_mod": anuncio.fecha_ult_mod,
        "fecha_publicacion": anuncio.fecha_publicacion,
        "autor": anuncio.autor.username,
    }

    return Response(data, status=200)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def eliminar_anuncio_admin(request, anuncio_id):
    try:
        anuncio_service.eliminar_anuncio_admin(request.user, anuncio_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response({"detail": "Anuncio eliminado"}, status=200)