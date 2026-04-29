from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.generic import RedirectView

from .views import (
    ActualizarTicketView,
    CrearTicketView,
    DetalleTicketView,
    EliminarTicketView,
    KanbanView,
    MisTicketsView,
    RoleBasedLoginView,
)


app_name = "tickets"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="tickets:mis_tickets", permanent=False), name="home"),
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("mis-tickets/", MisTicketsView.as_view(), name="mis_tickets"),
    path("ticket/crear/", CrearTicketView.as_view(), name="crear_ticket"),
    path("mis-tickets/<int:pk>/", DetalleTicketView.as_view(), name="detalle_ticket"),
    path("admin-panel/", KanbanView.as_view(), name="kanban"),
    path("admin-panel/ticket/<int:pk>/actualizar/", ActualizarTicketView.as_view(), name="actualizar_ticket"),
    path("admin-panel/ticket/<int:pk>/eliminar/", EliminarTicketView.as_view(), name="eliminar_ticket"),
]
