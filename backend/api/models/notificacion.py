from django.db import models


class Notificacion(models.Model):

    receptor = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="notificaciones_recibidas")

    class Meta:
        abstract = True

class SolicitudAmistad(Notificacion):
    emisor = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="solicitudes_amistad_enviadas")

class InvitacionPartida(Notificacion):
    emisor = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="invitaciones_partida_enviadas")
    partida = models.ForeignKey("Partida", on_delete=models.CASCADE, related_name="invitaciones")