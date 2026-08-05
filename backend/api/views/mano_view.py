from ..utils.web_sockets import notificar_mesa_actualizada

from ..services import mano_service
from dataclasses import asdict
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_mesa(request, partida_id):
    """
    Endpoint para obtener la información de la mesa de juego de una partida.
    """
    try:
        mesa_info = mano_service.get_mesa(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    return Response(asdict(mesa_info), status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def repartir_cartas(request, partida_id):
    """
    Endpoint para repartir cartas a los jugadores de una partida.
    """
    try:
        mano_service.repartir_cartas(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)
    
    return Response({"detail": "Cartas repartidas correctamente."}, status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def jugador_quiere_cambiar(request, partida_id):
    """
    Endpoint para indicar que un jugador quiere cambiar cartas en la mano actual.
    """
    try:
        mano_service.jugador_quiere_cambiar(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)
    
    return Response({"detail": "Cambio de cartas registrado correctamente."}, status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def jugador_no_quiere_cambiar(request, partida_id):
    """
    Endpoint para indicar que un jugador no quiere cambiar cartas en la mano actual.
    """
    try:
        mano_service.jugador_no_quiere_cambiar(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)
    
    return Response({"detail": "Cambio de cartas registrado correctamente."}, status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def cambiar_cartas(request, partida_id):
    """
    Endpoint para cambiar cartas en la mano actual.
    """
    try:
        cartas_a_cambiar = request.data.get("cartas", [])
        mano_service.cambiar_cartas(request.user, partida_id, cartas_a_cambiar)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)
    
    return Response({"detail": "Cartas cambiadas correctamente."}, status=200)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def elegir_carta_comodin(request, partida_id):
    """
    Endpoint para elegir una carta comodín en la mano actual.
    """
    try:
        carta_comodin = request.data.get("carta_comodin", None)
        mano_service.elegir_carta_comodin(request.user, partida_id, carta_comodin)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)
    
    return Response({"detail": "Carta comodín elegida correctamente."}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_datos_carta(request, partida_id):
    """
    Endpoint para obtener los datos de una carta específica.
    """
    try:
        carta = request.GET.get("carta") or request.data.get("carta", None)
        datos_carta = mano_service.get_datos_carta(request.user, carta, partida_id)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    return Response(datos_carta, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def siguiente_mano(request, partida_id):
    """
    Endpoint para iniciar una nueva mano en la partida.
    """
    try:
        mano_service.siguiente_mano(request.user, partida_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)
    
    notificar_mesa_actualizada(partida_id)
    
    return Response({"detail": "Mano iniciada correctamente."}, status=200)