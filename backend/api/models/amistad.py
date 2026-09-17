from django.db import models

class Anuncio(models.Model):
    """Modelo para representar una amistad."""

    usuario1 = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="amistades_usuario1")
    usuario2 = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="amistades_usuario2")
    aceptada = models.BooleanField(default=False)  # Indica si la amistad ha sido aceptada

    