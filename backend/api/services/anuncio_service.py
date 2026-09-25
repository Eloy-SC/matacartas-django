

from time import timezone

from ..utils.exceptions import RegistrationError

from ..models.anuncio import Anuncio

from ..selectors.anuncio_selector import get_anuncio_by_id, list_anuncios_all, list_anuncios_publicos


def listar_anuncios_admin(actor):

    if not actor.is_staff:
        raise PermissionError("No tienes permiso para listar anuncios")

    return list_anuncios_all()

def listar_anuncios_publicos(actor):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar anuncios públicos")

    return list_anuncios_publicos()

def get_anuncio(actor, anuncio_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para obtener un anuncio")

    try:
        anuncio = Anuncio.objects.get(id=anuncio_id)
    except Anuncio.DoesNotExist:
        raise ValueError("No se encontró el anuncio")

    return anuncio

def crear_anuncio_admin(actor, *, titulo, subtitulo, descripcion):

    if not actor.is_staff:
        raise PermissionError("No tienes permiso para crear anuncios")

    anuncios_existentes = list_anuncios_all()
    if anuncios_existentes.filter(titulo=titulo).exists():
        raise RegistrationError("Ya existe un anuncio con ese título")
    if len(anuncios_existentes) >= 20:
        raise RegistrationError("Ya existen 20 aununcios, es necesario borrar alguno para poder crear uno nuevo")

    anuncio = Anuncio(
        titulo=titulo,
        subtitulo=subtitulo,
        descripcion=descripcion,
        fecha_publicacion=None,
        autor=actor,
    )
    anuncio.save()

    return anuncio

def editar_anuncio_admin(actor, anuncio_id, *, titulo, subtitulo, descripcion):
    
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para editar anuncios")

    anuncio = get_anuncio_by_id(anuncio_id)
    if anuncio is None:
        raise ValueError("No se encontró el anuncio a editar")
    if anuncio.fecha_publicacion is not None:
        raise ValueError("No se puede editar un anuncio que ya ha sido publicado")

    anuncios_existentes = list_anuncios_all().exclude(id=anuncio_id)
    if anuncios_existentes.filter(titulo=titulo).exists():
        raise RegistrationError("Ya existe un anuncio con ese título")

    anuncio.titulo = titulo
    anuncio.subtitulo = subtitulo
    anuncio.descripcion = descripcion
    anuncio.fecha_ult_mod = timezone.now()
    anuncio.save()

    return anuncio

def publicar_anuncio_admin(actor, anuncio_id):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para publicar anuncios")

    anuncio = get_anuncio_by_id(anuncio_id)
    if anuncio is None:
        raise ValueError("No se encontró el anuncio a publicar")

    anuncio.fecha_publicacion = timezone.now()
    anuncio.save()

    return anuncio

def eliminar_anuncio_admin(actor, anuncio_id):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para eliminar anuncios")

    anuncio = get_anuncio_by_id(anuncio_id)
    if anuncio is None:
        raise ValueError("No se encontró el anuncio a eliminar")

    anuncio.delete()