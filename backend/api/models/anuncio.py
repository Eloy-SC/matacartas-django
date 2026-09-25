from django.db import models

class Anuncio(models.Model):
    """Modelo para representar un anuncio."""

    titulo = models.CharField(max_length=80, null=False)
    subtitulo = models.CharField(max_length=120, null=False)
    descripcion = models.TextField(null=False)
    
    fecha_ult_mod = models.DateTimeField(auto_now_add=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    autor = models.ForeignKey("Usuario", on_delete=models.CASCADE)