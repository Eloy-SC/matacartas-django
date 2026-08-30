from django.db import models


class ConfiguracionGlobal(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)

    rango_minimo_crear_torneo = models.ForeignKey("Rango", 
                                    on_delete=models.SET_NULL, 
                                    null=True, blank=True, 
                                    default=None,
                                    related_name="rango_minimo_crear_torneo")