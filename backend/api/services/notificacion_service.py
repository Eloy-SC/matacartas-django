from ..selectors.notificacion_selector import get_solicitud_amistad_by_id, get_solicitud_amistad_by_usuario_ids
from ..selectors.amistad_selector import get_amistad_by_usuario_ids

from ..models.notificacion import SolicitudAmistad
from ..models import Amistad

def listar_notificaciones(actor):
    pass

def enviar_solicitud_amistad(actor, objetivo_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para enviar solicitudes de amistad")

    if actor.id == objetivo_id:
        raise ValueError("No puedes enviarte una solicitud de amistad a ti mismo")

    # Verificar si ya existe una amistad entre los usuarios
    amistad_existente = get_amistad_by_usuario_ids(actor.id, objetivo_id)
    if amistad_existente:
        raise ValueError("Ya eres amigo de este usuario")

    # Verificar si ya existe una solicitud de amistad pendiente
    solicitud_existente = get_solicitud_amistad_by_usuario_ids(actor.id, objetivo_id)
    if solicitud_existente:
        raise ValueError("Ya has enviado una solicitud de amistad a este usuario")

    # Crear la nueva solicitud de amistad
    nueva_solicitud = SolicitudAmistad.objects.create(
        receptor_id=objetivo_id,
        emisor_id=actor.id
    )
    return nueva_solicitud

def contestar_solicitud_amistad(actor, solicitud_id, aceptar=False):
    if not actor.is_active:
        if aceptar:
            raise PermissionError("No tienes permiso para aceptar solicitudes de amistad")
        else:
            raise PermissionError("No tienes permiso para rechazar solicitudes de amistad")

    solicitud = get_solicitud_amistad_by_id(solicitud_id)
    if not solicitud:
        raise ValueError("No se encontró la solicitud de amistad")
    
    # Si se acepta la solicitud, crear la amistad entre los usuarios
    if aceptar:
        Amistad.objects.create(usuario1_id=solicitud.emisor_id, usuario2_id=solicitud.receptor_id)

    # Eliminar la solicitud de amistad
    solicitud.delete()