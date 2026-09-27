from django.contrib.auth import get_user_model
from django.test import TestCase

from api.models.amistad import Amistad
from api.services import amistad_service


class AmistadServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="amistad_user",
            password="pass-123",
            email="amistad_user@example.com",
            nombre="Usuario Amistad",
        )
        self.friend = User.objects.create_user(
            username="amistad_friend",
            password="pass-123",
            email="amistad_friend@example.com",
            nombre="Amigo",
        )
        Amistad.objects.create(usuario1=self.user, usuario2=self.friend)

    def test_listar_amigos_paginated_returns_friend(self):
        result = amistad_service.listar_amigos_paginated(self.user)

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["nombre"], "Amigo")

    def test_eliminar_amigo_removes_friendship(self):
        amistad_service.eliminar_amigo(self.user, self.friend.id)

        self.assertFalse(Amistad.objects.exists())

    def test_listar_amigos_paginated_filters_by_name(self):
        result = amistad_service.listar_amigos_paginated(self.user, search="Amigo")

        self.assertEqual(result["total"], 1)

    def test_listar_usuarios_busqueda_excludes_existing_friend(self):
        result = amistad_service.listar_usuarios_busqueda_amistad(self.user)

        self.assertFalse(any(item["id"] == self.friend.id for item in result["items"]))

    def test_listar_amigos_requires_active_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        with self.assertRaises(PermissionError):
            amistad_service.listar_amigos_paginated(self.user)

    def test_eliminar_amigo_raises_when_friendship_is_missing(self):
        amistad_service.eliminar_amigo(self.user, self.friend.id)

        with self.assertRaises(ValueError):
            amistad_service.eliminar_amigo(self.user, self.friend.id)
