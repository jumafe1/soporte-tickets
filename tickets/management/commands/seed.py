from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tickets.models import Categoria, Ticket


class Command(BaseCommand):
    help = "Crea usuarios, categorias y tickets de prueba de forma idempotente."

    def handle(self, *args, **options):
        users = {
            "admin": self._get_or_create_user("admin", "admin123", is_staff=True, is_superuser=True),
            "user1": self._get_or_create_user("user1", "user1123"),
            "user2": self._get_or_create_user("user2", "user2123"),
        }

        category_names = [
            "Soporte técnico",
            "Facturación",
            "Cuenta y acceso",
            "Consulta general",
            "Reporte de error",
        ]
        categories = {}
        for name in category_names:
            category, _ = Categoria.objects.get_or_create(nombre=name)
            categories[name] = category

        ticket_data = [
            {
                "titulo": "No puedo iniciar sesión",
                "descripcion": "El sistema no acepta mi clave desde esta mañana.",
                "estado": Ticket.Estado.ABIERTO,
                "prioridad": Ticket.Prioridad.ALTA,
                "usuario": users["user1"],
                "categoria": categories["Cuenta y acceso"],
            },
            {
                "titulo": "Error al generar factura",
                "descripcion": "La factura del mes actual aparece con valores duplicados.",
                "estado": Ticket.Estado.EN_ESPERA,
                "prioridad": Ticket.Prioridad.CRITICA,
                "usuario": users["user1"],
                "categoria": categories["Facturación"],
                "respuesta_admin": "Estamos validando el historial de pagos.",
            },
            {
                "titulo": "Consulta sobre plan activo",
                "descripcion": "Necesito confirmar las condiciones del plan contratado.",
                "estado": Ticket.Estado.APROBADO,
                "prioridad": Ticket.Prioridad.MEDIA,
                "usuario": users["user1"],
                "categoria": categories["Consulta general"],
                "respuesta_admin": "Tu plan activo fue confirmado correctamente.",
            },
            {
                "titulo": "Aplicacion lenta",
                "descripcion": "Las pantallas tardan mucho en cargar durante la tarde.",
                "estado": Ticket.Estado.ABIERTO,
                "prioridad": Ticket.Prioridad.MEDIA,
                "usuario": users["user2"],
                "categoria": categories["Soporte técnico"],
            },
            {
                "titulo": "Boton guardar falla",
                "descripcion": "Al guardar cambios aparece un mensaje de error inesperado.",
                "estado": Ticket.Estado.RECHAZADO,
                "prioridad": Ticket.Prioridad.BAJA,
                "usuario": users["user2"],
                "categoria": categories["Reporte de error"],
                "respuesta_admin": "No logramos reproducir el problema con los datos enviados.",
            },
            {
                "titulo": "Cambio de correo",
                "descripcion": "Quiero actualizar el correo principal de mi cuenta.",
                "estado": Ticket.Estado.EN_ESPERA,
                "prioridad": Ticket.Prioridad.ALTA,
                "usuario": users["user2"],
                "categoria": categories["Cuenta y acceso"],
                "respuesta_admin": "Esperamos confirmación de identidad para continuar.",
            },
        ]

        created_count = 0
        for data in ticket_data:
            defaults = data.copy()
            titulo = defaults.pop("titulo")
            usuario = defaults.pop("usuario")
            _, created = Ticket.objects.get_or_create(
                titulo=titulo,
                usuario=usuario,
                defaults=defaults,
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed finalizado. Usuarios: {len(users)}, categorias: {len(categories)}, tickets nuevos: {created_count}."
            )
        )

    def _get_or_create_user(self, username, password, is_staff=False, is_superuser=False):
        user, _ = User.objects.get_or_create(username=username)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()
        return user
