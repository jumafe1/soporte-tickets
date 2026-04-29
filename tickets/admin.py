from django.contrib import admin

from .models import Categoria, Ticket


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre"]
    search_fields = ["nombre"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["titulo", "usuario", "categoria", "estado", "prioridad", "fecha_creacion"]
    list_filter = ["estado", "prioridad", "categoria"]
    search_fields = ["titulo", "usuario__username"]
    list_editable = ["estado", "prioridad"]
