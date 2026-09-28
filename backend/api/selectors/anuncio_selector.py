from ..models.anuncio import Anuncio

def list_anuncios_all():
    return Anuncio.objects.all()

def get_anuncio_by_id(anuncio_id):
    return Anuncio.objects.get(id=anuncio_id)

def list_anuncios_publicos():
    return Anuncio.objects.filter(fecha_publicacion__isnull=False).order_by('-fecha_publicacion')