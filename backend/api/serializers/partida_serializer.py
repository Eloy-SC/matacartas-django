import re

from rest_framework import serializers

from ..selectors import partida_selector, rango_selector
from ..models.partida import Partida


def _nombre_field() -> serializers.CharField:
	return serializers.CharField(
		required=True,
		allow_blank=False,
		max_length=40,
		error_messages={
			"required": "Falta el titulo de la partida",
			"blank": "Falta el titulo de la partida",
			"max_length": "El titulo es demasiado largo (max. 40 caracteres)",
		},
	)


def _num_jugadores_field() -> serializers.IntegerField:
	return serializers.IntegerField(
		required=True,
		min_value=2,
		max_value=6,
		error_messages={
			"required": "Falta el numero de jugadores",
			"invalid": "El numero de jugadores no es valido",
			"min_value": "El numero de jugadores minimo es 2",
			"max_value": "El numero de jugadores maximo es 6",
		},
	)


def _longitud_field() -> serializers.ChoiceField:
	return serializers.ChoiceField(
		choices=Partida.LongitudPartida.choices,
		required=False,
		default=Partida.LongitudPartida.NORMAL,
		error_messages={
			"invalid_choice": "La longitud no es valida",
		},
	)


def _cartas_especiales_field() -> serializers.BooleanField:
	return serializers.BooleanField(required=False, default=True)


def _tickets_field() -> serializers.BooleanField:
	return serializers.BooleanField(required=False, default=True)


def _tiempo_max_turno_field() -> serializers.IntegerField:
	return serializers.IntegerField(
		required=False,
		min_value=20,
		max_value=180,
		default=90,
		error_messages={
			"invalid": "El tiempo maximo no es valido",
			"min_value": "El tiempo maximo debe ser igual o mayor que 20",
			"max_value": "El tiempo maximo debe ser igual o menor que 180",
		},
	)


def _privada_field() -> serializers.BooleanField:
	return serializers.BooleanField(required=False, default=False)


def _clave_field() -> serializers.CharField:
	return serializers.CharField(
		required=False,
		allow_blank=True,
		allow_null=True,
		max_length=20,
		error_messages={
			"max_length": "La clave es demasiado larga (max. 20 caracteres)",
		},
	)


def _rango_id_field(*, field_label: str) -> serializers.IntegerField:
	return serializers.IntegerField(
		required=False,
		allow_null=True,
		error_messages={
			"invalid": f"El {field_label} no es valido",
		},
	)


class _UniquePartidaMixin:
	def validate_nombre(self, value: str) -> str:
		qs = partida_selector.get_partida_by_nombre(value)
		partida = self.context.get("partida")
		if partida is not None:
			qs = qs.exclude(id=partida.id)
		if qs.exists():
			raise serializers.ValidationError("El titulo ya existe")
		return value

	def validate_clave(self, value: str) -> str:
		if not value:
			return value
		if not re.fullmatch(r"[a-z0-9]+", value):
			raise serializers.ValidationError(
            "La clave sólo puede contener letras minúsculas y números"
        )
		qs = partida_selector.get_partida_by_clave(value)
		partida = self.context.get("partida")
		if partida is not None:
			qs = qs.exclude(id=partida.id)
		if qs.exists():
			raise serializers.ValidationError("La clave ya existe")
		return value

	def validate_rango_minimo_id(self, value):
		if value is None:
			return None
		if rango_selector.get_rango_by_id(value) is None:
			raise serializers.ValidationError("El rango minimo no existe")
		return value

	def validate_rango_maximo_id(self, value):
		if value is None:
			return None
		if rango_selector.get_rango_by_id(value) is None:
			raise serializers.ValidationError("El rango maximo no existe")
		return value


class _BasePartidaSerializer(serializers.Serializer):
	nombre = _nombre_field()
	num_jugadores = _num_jugadores_field()
	longitud = _longitud_field()
	cartas_especiales = _cartas_especiales_field()
	tickets = _tickets_field()
	tiempo_max_turno = _tiempo_max_turno_field()
	privada = _privada_field()
	clave = _clave_field()
	rango_minimo_id = _rango_id_field(field_label="rango minimo")
	rango_maximo_id = _rango_id_field(field_label="rango maximo")


class CrearPartidaSerializer(_UniquePartidaMixin, _BasePartidaSerializer):
	def validate(self, attrs):
		privada = attrs.get("privada", False)
		clave = attrs.get("clave")
		rango_minimo_id = attrs.get("rango_minimo_id")
		rango_maximo_id = attrs.get("rango_maximo_id")

		if privada and not clave:
			raise serializers.ValidationError({"clave": "Falta la clave para la partida privada"})

		if not privada:
			attrs["clave"] = None

		if rango_minimo_id is not None and rango_maximo_id is not None:
			rango_minimo = rango_selector.get_rango_by_id(rango_minimo_id)
			rango_maximo = rango_selector.get_rango_by_id(rango_maximo_id)
			if rango_minimo and rango_maximo:
				if rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
					raise serializers.ValidationError(
						{"rango_minimo_id": "El rango minimo no puede ser mayor que el rango maximo"}
					)

		return attrs

class EditarPartidaSerializer(_UniquePartidaMixin, _BasePartidaSerializer):
	def validate_nombre(self, value: str) -> str:
		return super().validate_nombre(value)

	def validate_clave(self, value: str) -> str:
		return super().validate_clave(value)

	def validate(self, attrs):
		privada = attrs.get("privada", False)
		clave = attrs.get("clave")
		rango_minimo_id = attrs.get("rango_minimo_id")
		rango_maximo_id = attrs.get("rango_maximo_id")

		if privada and not clave:
			raise serializers.ValidationError({"clave": "Falta la clave para la partida privada"})

		if not privada:
			attrs["clave"] = None

		if rango_minimo_id is not None and rango_maximo_id is not None:
			rango_minimo = rango_selector.get_rango_by_id(rango_minimo_id)
			rango_maximo = rango_selector.get_rango_by_id(rango_maximo_id)
			if rango_minimo and rango_maximo:
				if rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
					raise serializers.ValidationError(
						{"rango_minimo_id": "El rango minimo no puede ser mayor que el rango maximo"}
					)

		return attrs
