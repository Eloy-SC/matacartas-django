from django.contrib.auth import get_user_model
from django.test import TestCase

from api.services import user_service
from api.utils.exceptions import ActualizarPerfilError, RegistrationError


class UserServiceTests(TestCase):
    def setUp(self):
        UserModel = get_user_model()
        self.admin = UserModel.objects.create_user(
            username="admin",
            password="admin-pass-123",
            email="admin@example.com",
            nombre="Admin",
            is_staff=True,
        )
        self.other_admin = UserModel.objects.create_user(
            username="admin2",
            password="admin-pass-123",
            email="admin2@example.com",
            nombre="Admin2",
            is_staff=True,
        )
        self.user = UserModel.objects.create_user(
            username="user",
            password="user-pass-123",
            email="user@example.com",
            nombre="User",
        )

    def test_actualizar_perfil_updates_fields(self):
        updated = user_service.actualizar_perfil(
            self.user,
            username="user2",
            email="user2@example.com",
            nombre="User 2",
            imagen="https://example.com/u.png",
        )

        self.user.refresh_from_db()
        self.assertEqual(updated.id, self.user.id)
        self.assertEqual(self.user.username, "user2")
        self.assertEqual(self.user.email, "user2@example.com")
        self.assertEqual(self.user.nombre, "User 2")
        self.assertEqual(self.user.imagen, "https://example.com/u.png")
        self.assertTrue(self.user.check_password("user-pass-123"))

    def test_actualizar_perfil_updates_password_when_provided(self):
        user_service.actualizar_perfil(
            self.user,
            username="user",
            email="user@example.com",
            nombre="User",
            password="new-pass-123",
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-pass-123"))

    def test_actualizar_perfil_rejects_duplicate_username(self):
        with self.assertRaises(ActualizarPerfilError):
            user_service.actualizar_perfil(
                self.user,
                username="admin",
                email="user@example.com",
                nombre="User",
            )

    def test_actualizar_perfil_allows_duplicate_email(self):
        user_service.actualizar_perfil(
            self.user,
            username="user",
            email="admin@example.com",
            nombre="User",
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "admin@example.com")

    def test_listar_usuarios_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            user_service.listar_usuarios_admin(self.user, page=1, page_size=10)

    def test_listar_usuarios_admin_returns_paged_result(self):
        paged = user_service.listar_usuarios_admin(self.admin, page=1, page_size=2)
        self.assertEqual(paged["page"], 1)
        self.assertEqual(paged["page_size"], 2)
        self.assertGreaterEqual(paged["total"], 3)
        self.assertEqual(len(paged["items"]), 2)

    def test_get_usuario_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            user_service.get_usuario_admin(self.user, self.admin.id)

    def test_get_usuario_admin_returns_user(self):
        data = user_service.get_usuario_admin(self.admin, self.user.id)
        self.assertEqual(data["username"], "user")

    def test_crear_usuario_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            user_service.crear_usuario_admin(
                self.user,
                username="newuser",
                password="pass-123",
                email="newuser@example.com",
                nombre="New User",
                imagen=None,
                is_staff=False,
            )

    def test_crear_usuario_admin_creates_user(self):
        created = user_service.crear_usuario_admin(
            self.admin,
            username="newuser",
            password="pass-123",
            email="newuser@example.com",
            nombre="New User",
            imagen=None,
            is_staff=False,
        )

        self.assertEqual(created.username, "newuser")
        self.assertEqual(created.email, "newuser@example.com")
        self.assertFalse(created.is_staff)

    def test_crear_usuario_admin_allows_duplicate_email(self):
        created = user_service.crear_usuario_admin(
            self.admin,
            username="newuser",
            password="pass-123",
            email="user@example.com",
            nombre="New User",
            imagen=None,
            is_staff=False,
        )

        self.assertEqual(created.email, "user@example.com")

    def test_editar_usuario_admin_updates_user(self):
        updated = user_service.editar_usuario_admin(
            self.admin,
            self.user.id,
            username="user2",
            password="pass-456",
            email="user2@example.com",
            nombre="User 2",
            imagen=None,
            is_staff=False,
        )

        self.user.refresh_from_db()
        self.assertEqual(updated.id, self.user.id)
        self.assertEqual(self.user.username, "user2")
        self.assertEqual(self.user.email, "user2@example.com")
        self.assertTrue(self.user.check_password("pass-456"))

    def test_editar_usuario_admin_rejects_demote_last_admin(self):
        UserModel = get_user_model()
        only_admin = UserModel.objects.create_user(
            username="solo",
            password="pass-123",
            email="solo@example.com",
            nombre="Solo",
            is_staff=True,
        )
        with self.assertRaises(RegistrationError):
            user_service.editar_usuario_admin(
                only_admin,
                only_admin.id,
                username="solo",
                email="solo@example.com",
                nombre="Solo",
                imagen=None,
                is_staff=False,
            )

    def test_editar_usuario_admin_rejects_self_demote_when_other_admin_exists(self):
        with self.assertRaises(RegistrationError):
            user_service.editar_usuario_admin(
                self.admin,
                self.admin.id,
                username="admin",
                email="admin@example.com",
                nombre="Admin",
                imagen=None,
                is_staff=False,
            )

    def test_eliminar_usuario_admin_requires_staff(self):
        with self.assertRaises(PermissionError):
            user_service.eliminar_usuario_admin(self.user, self.user.id)

    def test_eliminar_usuario_admin_deletes_user(self):
        user_service.eliminar_usuario_admin(self.admin, self.user.id)
        UserModel = get_user_model()
        self.assertFalse(UserModel.objects.filter(id=self.user.id).exists())

    def test_eliminar_usuario_admin_raises_when_missing(self):
        with self.assertRaises(ValueError):
            user_service.eliminar_usuario_admin(self.admin, 9999)
