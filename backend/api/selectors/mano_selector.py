from ..models.catalogo_tickets import TICKETS

from ..models.partida_usuario import PartidaUsuario
from ..models.mano import Mano

def get_jugadores_en_mesa(id, orden_mesa):
    """
    Obtiene los PUs de los jugadores de la mesa, ordenados tal y como están ordenados los turnos en la mano.
    """
    partida_usuarios = PartidaUsuario.objects.filter(partida=id)
    indice = {color: i for i, color in enumerate(orden_mesa)}

    return sorted(partida_usuarios, key=lambda pu: indice[pu.color])

def get_mano_actual(partida_id):
    """
    Obtiene la mano actual de una partida.
    """
    return Mano.objects.filter(partida_id=partida_id).order_by('-num').first()

def get_tickets_clase_3():
    """
    Obtiene los tickets de clase 3.
    """
    return [ticket for ticket, info in TICKETS.items() if info.get("clase") == 3]

def get_tickets_clase_2():
    """
    Obtiene los tickets de clase 2.
    """
    return [ticket for ticket, info in TICKETS.items() if info.get("clase") == 2]

def get_tickets_clase_1():
    """
    Obtiene los tickets de clase 1.
    """
    return [ticket for ticket, info in TICKETS.items() if info.get("clase") == 1]

def get_tickets_clase_0():
    """
    Obtiene los tickets de clase 0.
    """
    return [ticket for ticket, info in TICKETS.items() if info.get("clase") == 0]