from rest_framework import serializers

from ..models import Rango


def _nombre_field() -> serializers.CharField:
    return serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=25,
        error_messages={
            "required": "Falta el nombre",
            "blank": "Falta el nombre",
            "max_length": "El nombre es demasiado largo (max. 25 caracteres)",
        },
    )


def _puntos_field(*, field_label: str) -> serializers.IntegerField:
    return serializers.IntegerField(
        required=True,
        error_messages={
            "required": f"Faltan los puntos {field_label}",
            "invalid": f"Los puntos {field_label} no son válidos",
        },
    )


class _UniqueRangoMixin:
    def validate_nombre(self, value: str) -> str:
        qs = Rango.objects.filter(nombre=value)
        rango = self.context.get("rango")
        if rango is not None:
            qs = qs.exclude(id=rango.id)
        if qs.exists():
            raise serializers.ValidationError("El nombre ya existe")
        return value

    def validate_puntos_minimos(self, value: int) -> int:
        qs = Rango.objects.filter(puntos_minimos=value)
        rango = self.context.get("rango")
        if rango is not None:
            qs = qs.exclude(id=rango.id)
        if qs.exists():
            raise serializers.ValidationError("Ya hay otro rango con esos puntos mínimos")
        return value

    def validate_puntos_maximos(self, value: int) -> int:
        qs = Rango.objects.filter(puntos_maximos=value)
        rango = self.context.get("rango")
        if rango is not None:
            qs = qs.exclude(id=rango.id)
        if qs.exists():
            raise serializers.ValidationError("Ya hay otro rango con esos puntos máximos")
        return value


class RangoSerializer(_UniqueRangoMixin, serializers.Serializer):
    nombre = _nombre_field()
    color = serializers.ChoiceField(choices=Rango.Color.choices, required=True)
    puntos_minimos = _puntos_field(field_label="minimos")
    puntos_maximos = _puntos_field(field_label="maximos")

    def validate(self, attrs):
        puntos_minimos = attrs.get("puntos_minimos")
        puntos_maximos = attrs.get("puntos_maximos")
        if puntos_minimos is not None and puntos_maximos is not None:
            if puntos_minimos > puntos_maximos:
                raise serializers.ValidationError(
                    {"detail": "Los puntos minimos no pueden ser mayores que los maximos"}
                )
        return attrs
