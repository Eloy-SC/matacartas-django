from ..selectors.amistad_selector import get_amistad_by_usuario_ids
from ..models import SolicitudAmistad

def enviar_solicitud_de_amistad(actor, objetivo_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para enviar solicitudes de amistad")

    if actor.id == objetivo_id:
        raise ValueError("No puedes enviarte una solicitud de amistad a ti mismo")

    # Verificar si ya existe una amistad entre los usuarios
    amistad_existente = get_amistad_by_usuario_ids(actor.id, objetivo_id)
    if amistad_existente:
        raise ValueError("Ya eres amigo de este usuario")

    # Verificar si ya existe una solicitud de amistad pendiente
    solicitud_existente = SolicitudAmistad.objects.filter(
        receptor_id=objetivo_id,
        emisor_id=actor.id
    ).first()
    if solicitud_existente:
        raise ValueError("Ya has enviado una solicitud de amistad a este usuario")

    # Crear la nueva solicitud de amistad
    nueva_solicitud = SolicitudAmistad.objects.create(
        receptor_id=objetivo_id,
        emisor_id=actor.id
    )
    return nueva_solicitud