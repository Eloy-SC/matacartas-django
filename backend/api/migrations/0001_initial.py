import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "password",
                    models.CharField(max_length=128, verbose_name="password"),
                ),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="email address"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined"),
                ),
                (
                    "nombre",
                    models.CharField(max_length=30),
                ),
                (
                    "puntuacion",
                    models.IntegerField(default=0),
                ),
                (
                    "imagen",
                    models.TextField(blank=True, null=True),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Rango",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=25, unique=True, null=False, blank=False)),
                (
                    "color",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("blanco", "Blanco"),
                            ("negro", "Negro"),
                            ("rosa", "Rosa"),
                            ("rojo_claro", "Rojo claro"),
                            ("rojo", "Rojo"),
                            ("rojo_oscuro", "Rojo oscuro"),
                            ("verde_claro", "Verde claro"),
                            ("verde_esperanza", "Verde esperanza"),
                            ("verde", "Verde"),
                            ("verde_oscuro", "Verde oscuro"),
                            ("azul_claro", "Azul claro"),
                            ("azul", "Azul"),
                            ("azul_oscuro", "Azul oscuro"),
                            ("azul_cian", "Azul cian"),
                            ("amarillo", "Amarillo"),
                            ("amarillo_dorado", "Dorado"),
                            ("amarillo_naranja", "Amarillo anaranjado"),
                            ("naranja", "Naranja"),
                            ("morado_claro", "Púrpura"),
                            ("morado", "Morado"),
                            ("morado_oscuro", "Morado oscuro"),
                            ("gris", "Gris"),
                            ("gris_plata", "Plata"),
                            ("marron_bronce", "Bronce"),
                            ("marron", "Marrón"),
                        ],
                        null=False,
                        blank=False,
                    ),
                ),
                ("puntos_minimos", models.IntegerField(null=False, unique=True)),
                ("puntos_maximos", models.IntegerField(null=False, unique=True)),
            ],
        ),
    ]
