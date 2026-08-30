from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.recompensa import Medalla
from api.services import medalla_service
from api.utils.exceptions import RegistrationError


class MedallaServiceTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.admin = UserModel.objects.create_user(
            username="admin_medallas",
            password="admin-pass-123",
            email="admin_medallas@example.com",
            nombre="Admin Medallas",
            is_staff=True,
        )
        self.user = UserModel.objects.create_user(
            username="user_medallas",
            password="user-pass-123",
            email="user_medallas@example.com",
            nombre="User Medallas",
        )

        self.medalla = Medalla.objects.create(
            nombre="Medalla Inicial",
            categoria=Medalla.CategoriaMedalla.BRONCE,
            imagen="https://example.com/bronze.png",
        )

    def test_listar_medallas_requires_active_user(self):
        self.user.is_active = False
        self.user.save()
        with self.assertRaises(PermissionError):
            medalla_service.listar_medallas(self.user)

    def test_listar_medallas_returns_values(self):
        medallas = list(medalla_service.listar_medallas(self.user))
        self.assertGreaterEqual(len(medallas), 1)
        self.assertIn("nombre", medallas[0])

    def test_get_medalla_requires_active_user(self):
        self.user.is_active = False
        self.user.save()
        with self.assertRaises(PermissionError):
            medalla_service.get_medalla(self.user, self.medalla.id)

    def test_get_medalla_returns_item(self):
        data = medalla_service.get_medalla(self.user, self.medalla.id)
        self.assertEqual(data["nombre"], "Medalla Inicial")

    def test_crear_medalla_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            medalla_service.crear_medalla_admin(
                self.user,
                nombre="Nueva",
                categoria=Medalla.CategoriaMedalla.ORO,
                imagen="",
            )

    def test_crear_medalla_admin_rejects_duplicate_name(self):
        with self.assertRaises(RegistrationError):
            medalla_service.crear_medalla_admin(
                self.admin,
                nombre="Medalla Inicial",
                categoria=Medalla.CategoriaMedalla.PLATA,
                imagen="",
            )

    def test_crear_medalla_admin_creates_medalla(self):
        medalla = medalla_service.crear_medalla_admin(
            self.admin,
            nombre="Nueva Medalla",
            categoria=Medalla.CategoriaMedalla.ORO,
            imagen="https://example.com/gold.png",
        )
        self.assertEqual(medalla.nombre, "Nueva Medalla")

    def test_editar_medalla_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            medalla_service.editar_medalla_admin(
                self.user,
                self.medalla.id,
                nombre="Medalla Actualizada",
                categoria=Medalla.CategoriaMedalla.PLATA,
                imagen="",
            )

    def test_editar_medalla_admin_raises_when_missing(self):
        with self.assertRaises(ValueError):
            medalla_service.editar_medalla_admin(
                self.admin,
                9999,
                nombre="Medalla Actualizada",
                categoria=Medalla.CategoriaMedalla.PLATA,
                imagen="",
            )

    def test_editar_medalla_admin_updates_medalla(self):
        updated = medalla_service.editar_medalla_admin(
            self.admin,
            self.medalla.id,
            nombre="Medalla Actualizada",
            categoria=Medalla.CategoriaMedalla.PLATA,
            imagen="https://example.com/silver.png",
        )
        self.assertEqual(updated.nombre, "Medalla Actualizada")

    def test_eliminar_medalla_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            medalla_service.eliminar_medalla_admin(self.user, self.medalla.id)

    def test_eliminar_medalla_admin_raises_when_missing(self):
        with self.assertRaises(ValueError):
            medalla_service.eliminar_medalla_admin(self.admin, 9999)

    def test_eliminar_medalla_admin_deletes_medalla(self):
        medalla_service.eliminar_medalla_admin(self.admin, self.medalla.id)
        self.assertFalse(Medalla.objects.filter(id=self.medalla.id).exists())
