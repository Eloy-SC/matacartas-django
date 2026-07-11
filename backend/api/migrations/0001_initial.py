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
                    models.CharField(max_length=40),
                ),
                (
                    "puntuacion",
                    models.IntegerField(default=0),
                ),
                (
                    "imagen",
                    models.TextField(blank=True, null=True, max_length=1000, default=None),
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
        migrations.CreateModel(
            name="Partida",
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
                ("nombre", models.CharField(max_length=40, unique=True, null=False, blank=False)),
                ("num_jugadores", models.IntegerField(null=False, default=2)),
                ("privada", models.BooleanField(default=False)),
                ("clave", models.CharField(max_length=20, unique=True, null=True, blank=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_inicio", models.DateTimeField(null=True, blank=True)),
                ("fecha_fin", models.DateTimeField(null=True, blank=True)),
                (
                    "longitud",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("corta", "Corta"),
                            ("normal", "Normal"),
                            ("larga", "Larga"),
                        ],
                        null=False,
                        blank=False,
                    ),
                ),
                ("cartas_especiales", models.BooleanField(default=True)),
                ("tickets", models.BooleanField(default=True)),
                ("tiempo_max_turno", models.IntegerField(null=False, default=90)),
                (
                    "rango_minimo",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.rango",
                    ),
                ),
                (
                    "rango_maximo",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.rango",
                    ),
                ),
                ("baraja", models.JSONField(default=list)),
                ("disposicion_jugadores", models.JSONField(default=list)),
                ("turno_actual", models.CharField(max_length=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="PartidaUsuario",
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
                    "partida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.partida",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.usuario",
                    ),
                ),
                ("creador", models.BooleanField(default=False)),
                ("listo", models.BooleanField(default=False)),
                ("color", models.CharField(
                        max_length=8,
                        choices=[
                            ("rojo", "Rojo"),
                            ("naranja", "Naranja"),
                            ("amarillo", "Amarillo"),
                            ("verde", "Verde"),
                            ("azul", "Azul"),
                            ("morado", "Morado"),
                        ],
                        null=False,
                        blank=False,
                    ),
                ),
                ("puntos", models.IntegerField(null=False, default=0)),
                ("cartas", models.JSONField(default=list)),
                ("carta_comodin", models.CharField(max_length=25, null=True, default=None)),
                ("acumulador_kills", models.IntegerField(null=False, default=0)),
                ("acumulador_deaths", models.IntegerField(null=False, default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Mano",
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
                    "partida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.partida",
                    ),
                ),
                ("num", models.IntegerField(null=False, default=1)),
            ],
        ),
        migrations.CreateModel(
            name="Ronda",
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
                    "mano",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.mano",
                    ),
                ),
                ("num", models.IntegerField(null=False, default=0)),
                ("cartas", models.JSONField(default=dict, null=True)),
            ],
        ),
    ]
