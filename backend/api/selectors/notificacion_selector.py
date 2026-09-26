

from ..models.notificacion import SolicitudAmistad



def get_solicitud_amistad_by_id(solicitud_id):
    return SolicitudAmistad.objects.filter(id=solicitud_id).first()

def get_solicitud_amistad_by_usuario_ids(emisor_id, receptor_id):
    return SolicitudAmistad.objects.filter(
        emisor_id=emisor_id,
        receptor_id=receptor_id
    ).first()