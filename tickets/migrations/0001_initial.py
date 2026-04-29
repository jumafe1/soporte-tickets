from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Categoria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "ordering": ["nombre"],
            },
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=200)),
                ("descripcion", models.TextField()),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("abierto", "Abierto"),
                            ("en_espera", "En espera"),
                            ("aprobado", "Aprobado"),
                            ("rechazado", "Rechazado"),
                        ],
                        default="abierto",
                        max_length=20,
                    ),
                ),
                (
                    "prioridad",
                    models.CharField(
                        choices=[
                            ("baja", "Baja"),
                            ("media", "Media"),
                            ("alta", "Alta"),
                            ("critica", "Crítica"),
                        ],
                        default="media",
                        max_length=20,
                    ),
                ),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("respuesta_admin", models.TextField(blank=True, null=True)),
                (
                    "categoria",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="tickets.categoria"),
                ),
                (
                    "usuario",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "ordering": ["-fecha_creacion"],
            },
        ),
    ]
