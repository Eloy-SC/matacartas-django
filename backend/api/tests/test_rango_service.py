from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.rango import Rango
from api.services import rango_service
from api.utils.exceptions import RegistrationError


class RangoServiceTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.admin = UserModel.objects.create_user(
            username="admin",
            password="admin-pass-123",
            email="admin@example.com",
            nombre="Admin",
            is_staff=True,
        )
        self.user = UserModel.objects.create_user(
            username="user",
            password="user-pass-123",
            email="user@example.com",
            nombre="User",
        )
        self.user.puntuacion = 10
        self.user.save()

        self.rango = Rango.objects.create(
            nombre="NovatoTest",
            color=Rango.Color.AZUL_CLARO,
            puntos_minimos=2000,
            puntos_maximos=2099,
        )
        self.rango2 = Rango.objects.create(
            nombre="ExpertoTest",
            color=Rango.Color.AZUL,
            puntos_minimos=2100,
            puntos_maximos=2199,
        )

    def test_listar_rangos_requires_active_user(self):
        self.user.is_active = False
        self.user.save()
        with self.assertRaises(PermissionError):
            rango_service.listar_rangos(self.user)

    def test_listar_rangos_returns_values(self):
        rangos = list(rango_service.listar_rangos(self.user))
        self.assertGreaterEqual(len(rangos), 2)
        self.assertIn("nombre", rangos[0])

    def test_get_rango_requires_active_user(self):
        self.user.is_active = False
        self.user.save()
        with self.assertRaises(PermissionError):
            rango_service.get_rango(self.user, self.rango.id)

    def test_get_rango_returns_item(self):
        data = rango_service.get_rango(self.user, self.rango.id)
        self.assertEqual(data["nombre"], "NovatoTest")

    def test_get_rango_de_usuario_returns_none_when_missing(self):
        rango = rango_service.get_rango_de_usuario(self.user, self.user.id)
        self.assertIsNone(rango)

    def test_get_rango_de_usuario_returns_range(self):
        self.user.puntuacion = 2150
        self.user.save()
        rango = rango_service.get_rango_de_usuario(self.user, self.user.id)
        self.assertEqual(rango.nombre, "ExpertoTest")

    def test_crear_rango_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            rango_service.crear_rango_admin(
                self.user,
                nombre="Veterano",
                color=Rango.Color.ROJO,
                puntos_minimos=200,
                puntos_maximos=299,
            )

    def test_crear_rango_admin_rejects_overlap(self):
        with self.assertRaises(RegistrationError):
            rango_service.crear_rango_admin(
                self.admin,
                nombre="Solapado",
                color=Rango.Color.ROJO_CLARO,
                puntos_minimos=2050,
                puntos_maximos=2150,
            )

    def test_crear_rango_admin_rejects_color_duplicate(self):
        with self.assertRaises(RegistrationError):
            rango_service.crear_rango_admin(
                self.admin,
                nombre="Otro",
                color=Rango.Color.AZUL_CLARO,
                puntos_minimos=3000,
                puntos_maximos=3099,
            )

    def test_crear_rango_admin_creates_rango(self):
        rango = rango_service.crear_rango_admin(
            self.admin,
            nombre="VeteranoTest",
            color=Rango.Color.AZUL_CIAN,
            puntos_minimos=3100,
            puntos_maximos=3199,
        )
        self.assertEqual(rango.nombre, "VeteranoTest")

    def test_editar_rango_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            rango_service.editar_rango_admin(
                self.user,
                self.rango.id,
                nombre="NovatoTest+",
                color=Rango.Color.AZUL_CLARO,
                puntos_minimos=2000,
                puntos_maximos=2089,
            )

    def test_editar_rango_admin_raises_when_missing(self):
        with self.assertRaises(ValueError):
            rango_service.editar_rango_admin(
                self.admin,
                9999,
                nombre="NovatoTest+",
                color=Rango.Color.AZUL_CLARO,
                puntos_minimos=2000,
                puntos_maximos=2089,
            )

    def test_editar_rango_admin_updates_rango(self):
        updated = rango_service.editar_rango_admin(
            self.admin,
            self.rango.id,
            nombre="NovatoTest+",
            color=Rango.Color.AZUL_CLARO,
            puntos_minimos=2000,
            puntos_maximos=2089,
        )
        self.assertEqual(updated.nombre, "NovatoTest+")

    def test_eliminar_rango_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            rango_service.eliminar_rango_admin(self.user, self.rango.id)

    def test_eliminar_rango_admin_raises_when_missing(self):
        with self.assertRaises(ValueError):
            rango_service.eliminar_rango_admin(self.admin, 9999)

    def test_eliminar_rango_admin_deletes_rango(self):
        rango_service.eliminar_rango_admin(self.admin, self.rango.id)
        self.assertFalse(Rango.objects.filter(id=self.rango.id).exists())
