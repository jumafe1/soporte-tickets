from django.contrib.auth.models import User
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Ticket(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = "abierto", "Abierto"
        EN_ESPERA = "en_espera", "En espera"
        APROBADO = "aprobado", "Aprobado"
        RECHAZADO = "rechazado", "Rechazado"

    class Prioridad(models.TextChoices):
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"
        CRITICA = "critica", "Crítica"

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ABIERTO,
    )
    prioridad = models.CharField(
        max_length=20,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    respuesta_admin = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo
