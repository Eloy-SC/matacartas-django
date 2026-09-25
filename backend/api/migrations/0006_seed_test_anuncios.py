from django.utils import timezone

from django.db import migrations


TEST_ANUNCIOS = [
    {
        "titulo": "Anuncio de prueba 1",
        "subtitulo": "Subtitulo de prueba 1",
        "descripcion": "Descripción de prueba 1",
        "fecha_publicacion": None,
    },
    {
        "titulo": "Anuncio de prueba 2",
        "subtitulo": "Subtitulo de prueba 2",
        "descripcion": "Descripción de prueba 2",
        "fecha_publicacion": None,
    },
    {
        "titulo": "Anuncio de prueba 3",
        "subtitulo": "Subtitulo de prueba 3",
        "descripcion": "Descripción de prueba 3",
        "fecha_publicacion": None,
    },
    {
        "titulo": "Anuncio de prueba 4",
        "subtitulo": "Subtitulo de prueba 4",
        "descripcion": "Descripción de prueba 4",
        "fecha_publicacion": None,
    },
    {
        "titulo": "Anuncio publicado con descripción larga",
        "subtitulo": "La descripción es todo lo larga que puede ser una descripción",
        "descripcion": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas vestibulum suscipit sem, a viverra nunc porta eu. Cras ultricies auctor tincidunt. Ut enim turpis, porta eu scelerisque in, hendrerit feugiat risus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Fusce consequat ultricies vehicula. Cras et sem magna. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc a sapien tincidunt, tempor massa sed, auctor odio. Sed cursus nibh nec fermentum commodo. Aenean rutrum blandit urna, quis feugiat orci luctus non. Sed mattis, felis sit amet vehicula luctus, lorem leo sodales turpis, a vehicula diam sem sit amet velit. Pellentesque convallis felis at lacus molestie gravida. Maecenas nec magna rhoncus, elementum tellus id, mattis ante. Morbi consequat, est a dapibus fringilla, eros felis mollis risus, non suscipit velit est ut ipsum. Vivamus consequat euismod faucibus. Nunc ultricies euismod elementum. Donec facilisis erat ut leo ligula.",
        "fecha_publicacion": str(timezone.now()),
    },
]

def seed_test_anuncios(apps, schema_editor):
    Anuncio = apps.get_model("api", "Anuncio")
    Usuario = apps.get_model("api", "Usuario")

    # Obtener un admin existente para asignarlo como autor
    autor = Usuario.objects.filter(is_staff=True).first()

    for anuncio_spec in TEST_ANUNCIOS:
        Anuncio.objects.update_or_create(
            titulo=anuncio_spec["titulo"],
            defaults={
                "subtitulo": anuncio_spec["subtitulo"],
                "descripcion": anuncio_spec["descripcion"],
                "fecha_publicacion": anuncio_spec["fecha_publicacion"],
                "autor": autor,
            },
        )

def unseed_test_anuncios(apps, schema_editor):
    Anuncio = apps.get_model("api", "Anuncio")
    titulos = [anuncio["titulo"] for anuncio in TEST_ANUNCIOS]
    Anuncio.objects.filter(titulo__in=titulos).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0005_seed_test_logros'),
    ]

    operations = [
        migrations.RunPython(seed_test_anuncios, reverse_code=unseed_test_anuncios),
    ]