

from rest_framework import serializers


def _titulo_field(*, required: bool) -> serializers.CharField:
    return serializers.CharField(
        required=required,
        allow_blank=not required,
        max_length=80,
        error_messages={
            "required": "Falta el título del anuncio",
            "blank": "Falta el título del anuncio",
            "max_length": "El título del anuncio es demasiado largo (máx. 80 caracteres)",
        },
    )

def _subtitulo_field(*, required: bool) -> serializers.CharField:
    return serializers.CharField(
        required=required,
        allow_blank=not required,
        max_length=120,
        error_messages={
            "required": "Falta el subtítulo del anuncio",
            "blank": "Falta el subtítulo del anuncio",
            "max_length": "El subtítulo del anuncio es demasiado largo (máx. 120 caracteres)",
        },
    )

class AnuncioSerializer(serializers.Serializer):
    titulo = _titulo_field(required=True)
    subtitulo = _subtitulo_field(required=True)
    descripcion = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1200,
        error_messages={
            "required": "Falta la descripción del anuncio",
            "blank": "Falta la descripción del anuncio",
            "max_length": "La descripción del anuncio es demasiado larga (máx. 1200 caracteres)",
        },
    )