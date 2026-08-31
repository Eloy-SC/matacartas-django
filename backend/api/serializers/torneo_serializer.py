from rest_framework import serializers

from ..models.torneo import Torneo
from ..selectors import rango_selector, medalla_selector


def _nombre_field() -> serializers.CharField:
    return serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=39,
        error_messages={
            "required": "Falta el nombre",
            "blank": "Falta el nombre",
            "max_length": "El nombre es demasiado largo (max. 39 caracteres)",
        },
    )


def _num_jug_field(field_label: str, *, required: bool = True, allow_null: bool = False):
    return serializers.IntegerField(
        required=required,
        allow_null=allow_null,
        min_value=2,
        max_value=6,
        error_messages={
            "required": f"Falta el número de jugadores de {field_label}",
            "invalid": f"El número de jugadores de {field_label} no es válido",
            "min_value": f"El número de jugadores de {field_label} debe ser al menos 2",
            "max_value": f"El número de jugadores de {field_label} no puede ser mayor a 6",
            "null": f"El número de jugadores de {field_label} no puede ser nulo",
        },
    )


def _rango_id_field(field_label: str):
    return serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        error_messages={
            "invalid": f"El {field_label} no es válido",
            "min_value": f"El {field_label} no es válido",
        },
    )


def _medalla_id_field(field_label: str):
    return serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        error_messages={
            "invalid": f"La {field_label} no es válida",
            "min_value": f"La {field_label} no es válida",
        },
    )


class TorneoSerializer(serializers.Serializer):
    nombre = _nombre_field()
    rango_minimo_id = _rango_id_field("rango mínimo")
    rango_maximo_id = _rango_id_field("rango máximo")
    num_jug_fin = _num_jug_field("la final")
    num_jug_sem = _num_jug_field("las semifinales")
    num_jug_cua = _num_jug_field("los cuartos", required=False, allow_null=True)
    num_jug_oct = _num_jug_field("los octavos", required=False, allow_null=True)
    partidas_longitud = serializers.ChoiceField(
        choices=Torneo.LongitudPartidaDeTorneo.choices,
        required=True,
        error_messages={
            "required": "Falta la longitud de partida",
            "invalid_choice": "La longitud de partida no es válida",
        },
    )
    partidas_cartas_especiales = serializers.BooleanField(required=True)
    partidas_tickets = serializers.BooleanField(required=True)
    partidas_tiempo_max_turno = serializers.IntegerField(
        required=True,
        min_value=20,
        max_value=180,
        error_messages={
            "required": "Falta el tiempo máximo por turno",
            "invalid": "El tiempo máximo por turno no es válido",
            "min_value": "El tiempo máximo por turno debe ser al menos 20 segundos",
            "max_value": "El tiempo máximo por turno no puede ser mayor a 180 segundos",
        },
    )
    desempate_mayor_punt = serializers.BooleanField(required=True)
    medalla_primer_puesto_id = _medalla_id_field("medalla de primer puesto")
    medalla_segundo_puesto_id = _medalla_id_field("medalla de segundo puesto")
    medalla_tercer_puesto_id = _medalla_id_field("medalla de tercer puesto")

    def validate_nombre(self, value: str) -> str:
        qs = Torneo.objects.filter(nombre=value)
        torneo = self.context.get("torneo")
        if torneo is not None:
            qs = qs.exclude(id=torneo.id)
        if qs.exists():
            raise serializers.ValidationError("El nombre ya existe")
        return value

    def validate_rango_minimo_id(self, value):
        if value is None:
            return None
        if rango_selector.get_rango_by_id(value) is None:
            raise serializers.ValidationError("El rango mínimo no existe")
        return value

    def validate_rango_maximo_id(self, value):
        if value is None:
            return None
        if rango_selector.get_rango_by_id(value) is None:
            raise serializers.ValidationError("El rango máximo no existe")
        return value

    def validate_medalla_primer_puesto_id(self, value):
        if value is None:
            return None
        if medalla_selector.get_medalla_by_id(value) is None:
            raise serializers.ValidationError("La medalla de primer puesto no existe")
        return value

    def validate_medalla_segundo_puesto_id(self, value):
        if value is None:
            return None
        if medalla_selector.get_medalla_by_id(value) is None:
            raise serializers.ValidationError("La medalla de segundo puesto no existe")
        return value

    def validate(self, attrs):
        rango_minimo_id = attrs.get("rango_minimo_id")
        rango_maximo_id = attrs.get("rango_maximo_id")

        if rango_minimo_id is not None and rango_maximo_id is not None:
            rango_minimo = rango_selector.get_rango_by_id(rango_minimo_id)
            rango_maximo = rango_selector.get_rango_by_id(rango_maximo_id)
            if rango_minimo and rango_maximo:
                if rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
                    raise serializers.ValidationError(
                        {"rango_minimo_id": "El rango mínimo no puede ser mayor que el rango máximo"}
                    )

        return attrs
