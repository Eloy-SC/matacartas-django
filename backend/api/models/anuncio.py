from django.db import models

class Anuncio(models.Model):
    """Modelo para representar un anuncio."""

    titulo = models.CharField(max_length=80, null=False)
    subtitulo = models.CharField(max_length=120, null=False)
    descripcion = models.TextField(null=False)
    publicado = models.BooleanField(default=False)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    autor = models.ForeignKey("Usuario", on_delete=models.CASCADE)