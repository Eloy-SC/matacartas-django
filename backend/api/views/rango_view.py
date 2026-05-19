from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.utils.exceptions import RegistrationError
from ..models.rango import Rango
from ..serializers.rango_serializer import RangoSerializer
from ..services import rango_service

@api_view(["GET"])
@permission_classes([])
def listar_rangos(request):
    try:
        rangos = rango_service.listar_rangos(request.user)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    data = [
        {
            "id": rango["id"],
            "nombre": rango["nombre"],
            "color": rango["color"],
            "puntos_minimos": rango["puntos_minimos"],
            "puntos_maximos": rango["puntos_maximos"],
        }
        for rango in rangos
    ]
    return Response(data, status=200)


@api_view(["GET"])
@permission_classes([])
def get_rango(request, rango_id):
    try:
        rango = rango_service.get_rango(request.user, rango_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    if not rango:
        return Response({"detail": "Rango no encontrado"}, status=404)

    data = {
        "id": rango["id"],
        "nombre": rango["nombre"],
        "color": rango["color"],
        "puntos_minimos": rango["puntos_minimos"],
        "puntos_maximos": rango["puntos_maximos"],
    }

    return Response(data, status=200)

@api_view(["GET"])
@permission_classes([])
def get_rango_de_usuario(request, user_id):
    try:
        rango = rango_service.get_rango_de_usuario(request.user, user_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    if not rango:
        return Response({"detail": "Rango no encontrado"}, status=404)

    data = {
        "id": rango.id,
        "nombre": rango.nombre,
        "color": rango.color,
        "puntos_minimos": rango.puntos_minimos,
        "puntos_maximos": rango.puntos_maximos,
    }

    return Response(data, status=200)

@api_view(["POST"])
@permission_classes([])
def crear_rango_admin(request):
    serializer = RangoSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        rango = rango_service.crear_rango_admin(request.user, **serializer.validated_data)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)

    return Response(
        {
            "id": rango.id,
            "nombre": rango.nombre,
            "detail": "Rango creado",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT"])
@permission_classes([])
def editar_rango_admin(request, rango_id):
    target_rango = Rango.objects.filter(id=rango_id).first()
    if target_rango is None:
        return Response({"detail": "Rango no encontrado"}, status=404)

    serializer = RangoSerializer(data=request.data, context={"rango": target_rango})

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        rango = rango_service.editar_rango_admin(
            request.user, rango_id, **serializer.validated_data
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response(
        {
            "id": rango.id,
            "nombre": rango.nombre,
            "detail": "Rango actualizado",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([])
def eliminar_rango_admin(request, rango_id):
    try:
        rango_service.eliminar_rango_admin(request.user, rango_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response({"detail": "Rango eliminado"}, status=status.HTTP_200_OK)