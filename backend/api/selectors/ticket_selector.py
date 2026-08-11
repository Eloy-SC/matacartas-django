from ..models.catalogo_tickets import TICKETS

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