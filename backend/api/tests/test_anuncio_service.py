from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.anuncio import Anuncio
from api.services import anuncio_service


class AnuncioServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="anuncio_admin",
            password="pass-123",
            email="anuncio_admin@example.com",
            nombre="Admin Anuncios",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="anuncio_user",
            password="pass-123",
            email="anuncio_user@example.com",
            nombre="Usuario Anuncios",
        )

    def test_crear_anuncio_admin_creates_draft(self):
        anuncio = anuncio_service.crear_anuncio_admin(
            self.admin,
            titulo="Aviso",
            subtitulo="Subtitulo",
            descripcion="Descripcion",
        )

        self.assertEqual(anuncio.titulo, "Aviso")
        self.assertIsNone(anuncio.fecha_publicacion)

    def test_listar_anuncios_publicos_requires_active_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        with self.assertRaises(PermissionError):
            anuncio_service.listar_anuncios_publicos(self.user)

    def test_listar_anuncios_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            anuncio_service.listar_anuncios_admin(self.user)

    def test_get_anuncio_raises_when_missing(self):
        with self.assertRaises(ValueError):
            anuncio_service.get_anuncio(self.user, 9999)

    def test_publicar_anuncio_sets_publication_date(self):
        anuncio = anuncio_service.crear_anuncio_admin(
            self.admin,
            titulo="Aviso publicable",
            subtitulo="Subtitulo",
            descripcion="Descripcion",
        )

        anuncio_service.publicar_anuncio_admin(self.admin, anuncio.id)

        anuncio.refresh_from_db()
        self.assertIsNotNone(anuncio.fecha_publicacion)

    def test_eliminar_anuncio_removes_item(self):
        anuncio = anuncio_service.crear_anuncio_admin(
            self.admin,
            titulo="Aviso eliminable",
            subtitulo="Subtitulo",
            descripcion="Descripcion",
        )

        anuncio_service.eliminar_anuncio_admin(self.admin, anuncio.id)

        self.assertFalse(Anuncio.objects.filter(id=anuncio.id).exists())
