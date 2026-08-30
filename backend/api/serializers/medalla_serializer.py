from rest_framework import serializers

from ..models.recompensa import Medalla


def _nombre_field() -> serializers.CharField:
    return serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=40,
        error_messages={
            "required": "Falta el nombre",
            "blank": "Falta el nombre",
            "max_length": "El nombre es demasiado largo (max. 40 caracteres)",
        },
    )


class MedallaSerializer(serializers.Serializer):
    nombre = _nombre_field()
    categoria = serializers.ChoiceField(
        choices=Medalla.CategoriaMedalla.choices,
        required=True,
        error_messages={
            "required": "Falta la categoria",
            "invalid_choice": "Categoria no valida",
        },
    )
    imagen = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=1000,
        error_messages={
            "max_length": "La imagen es demasiado larga (max. 1000 caracteres)",
        },
    )

    def validate_nombre(self, value: str) -> str:
        qs = Medalla.objects.filter(nombre=value)
        medalla = self.context.get("medalla")
        if medalla is not None:
            qs = qs.exclude(id=medalla.id)
        if qs.exists():
            raise serializers.ValidationError("El nombre ya existe")
        return value
