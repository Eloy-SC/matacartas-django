from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (
		(
			"Perfil",
			{
				"fields": (
					"nombre",
					"puntuacion",
					"imagen",
				)
			},
		),
	)

	add_fieldsets = UserAdmin.add_fieldsets + (
		(
			"Perfil",
			{
				"fields": (
					"nombre",
					"imagen",
				)
			},
		),
	)

	list_display = UserAdmin.list_display + (
		"nombre",
		"puntuacion",
	)
