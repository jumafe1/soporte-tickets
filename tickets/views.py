import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import TicketForm
from .models import Categoria, Ticket


RESPUESTA_ADMIN_MAX_LENGTH = 150


class RoleBasedLoginView(LoginView):
    template_name = "tickets/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy("tickets:kanban")
        return reverse_lazy("tickets:mis_tickets")


class StaffRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            return redirect("tickets:mis_tickets")
        return super().dispatch(request, *args, **kwargs)


class MisTicketsView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/mis_tickets.html"
    context_object_name = "tickets"

    def get_queryset(self):
        queryset = (
            Ticket.objects.filter(usuario=self.request.user)
            .select_related("categoria", "usuario")
            .order_by("-fecha_creacion")
        )
        estado = self.request.GET.get("estado")
        if estado in Ticket.Estado.values:
            queryset = queryset.filter(estado=estado)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conteos_estado = {
            item["estado"]: item["total"]
            for item in Ticket.objects.filter(usuario=self.request.user)
            .values("estado")
            .annotate(total=Count("id"))
        }
        context["conteo"] = context["tickets"].count()
        context["filtros_estado"] = [
            {"valor": valor, "label": label}
            for valor, label in Ticket.Estado.choices
            if conteos_estado.get(valor, 0) > 0
        ]
        return context


class CrearTicketView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "tickets/crear_ticket.html"
    success_url = reverse_lazy("tickets:mis_tickets")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.estado = Ticket.Estado.ABIERTO
        return super().form_valid(form)


class DetalleTicketView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "tickets/detalle_ticket.html"
    context_object_name = "ticket"

    def get_queryset(self):
        return Ticket.objects.select_related("categoria", "usuario")

    def get_object(self, queryset=None):
        ticket = super().get_object(queryset)
        if ticket.usuario != self.request.user:
            raise PermissionDenied("No puedes ver tickets de otro usuario.")
        return ticket


class KanbanView(StaffRequiredMixin, TemplateView):
    template_name = "tickets/kanban.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_queryset = Ticket.objects.select_related("categoria", "usuario").order_by("-fecha_creacion")
        categorias = Categoria.objects.order_by("nombre").annotate(ticket_count=Count("ticket"))
        context.update(
            {
                "abiertos": base_queryset.filter(estado=Ticket.Estado.ABIERTO),
                "en_espera": base_queryset.filter(estado=Ticket.Estado.EN_ESPERA),
                "aprobados": base_queryset.filter(estado=Ticket.Estado.APROBADO),
                "rechazados": base_queryset.filter(estado=Ticket.Estado.RECHAZADO),
                "categorias": categorias,
            }
        )
        return context


class CategoriaListCreateView(StaffRequiredMixin, View):
    http_method_names = ["get", "post"]

    def get(self, request):
        categorias = list(
            Categoria.objects.order_by("nombre")
            .annotate(ticket_count=Count("ticket"))
            .values("id", "nombre", "ticket_count")
        )
        return JsonResponse({"success": True, "categorias": categorias})

    def post(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "JSON invalido."}, status=400)

        nombre = (payload.get("nombre") or "").strip()
        if not nombre:
            return JsonResponse({"success": False, "error": "El nombre de la categoría es obligatorio."}, status=400)
        if len(nombre) > 100:
            return JsonResponse({"success": False, "error": "La categoría no puede superar 100 caracteres."}, status=400)
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({"success": False, "error": "Ya existe una categoría con ese nombre."}, status=400)

        categoria = Categoria.objects.create(nombre=nombre)
        return JsonResponse(
            {
                "success": True,
                "categoria": {
                    "id": categoria.id,
                    "nombre": categoria.nombre,
                    "ticket_count": 0,
                },
            }
        )


class CategoriaUpdateDeleteView(StaffRequiredMixin, View):
    http_method_names = ["post", "delete"]

    def post(self, request, pk):
        try:
            categoria = Categoria.objects.get(pk=pk)
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except Categoria.DoesNotExist:
            return JsonResponse({"success": False, "error": "Categoría no encontrada."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "JSON invalido."}, status=400)

        nombre = (payload.get("nombre") or "").strip()
        if not nombre:
            return JsonResponse({"success": False, "error": "El nombre de la categoría es obligatorio."}, status=400)
        if len(nombre) > 100:
            return JsonResponse({"success": False, "error": "La categoría no puede superar 100 caracteres."}, status=400)
        if Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=categoria.pk).exists():
            return JsonResponse({"success": False, "error": "Ya existe una categoría con ese nombre."}, status=400)

        categoria.nombre = nombre
        categoria.save(update_fields=["nombre"])
        return JsonResponse(
            {
                "success": True,
                "categoria": {
                    "id": categoria.id,
                    "nombre": categoria.nombre,
                    "ticket_count": categoria.ticket_set.count(),
                },
            }
        )

    def delete(self, request, pk):
        try:
            categoria = Categoria.objects.get(pk=pk)
            if categoria.ticket_set.exists():
                return JsonResponse(
                    {
                        "success": False,
                        "error": "No se puede eliminar esta categoría porque está asignada a uno o más tickets.",
                    },
                    status=400,
                )
            categoria.delete()
        except Categoria.DoesNotExist:
            return JsonResponse({"success": False, "error": "Categoría no encontrada."}, status=400)

        return JsonResponse({"success": True, "categoria_id": pk})


class ActualizarTicketView(StaffRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "error": "Ticket no encontrado."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "JSON invalido."}, status=400)

        if not isinstance(payload, dict):
            return JsonResponse({"success": False, "error": "El cuerpo debe ser un objeto JSON."}, status=400)

        update_fields = []

        if "estado" in payload:
            estado = payload["estado"]
            if estado not in Ticket.Estado.values:
                return JsonResponse({"success": False, "error": "Estado invalido."}, status=400)
            ticket.estado = estado
            update_fields.append("estado")

        if "prioridad" in payload:
            prioridad = payload["prioridad"]
            if prioridad not in Ticket.Prioridad.values:
                return JsonResponse({"success": False, "error": "Prioridad invalida."}, status=400)
            ticket.prioridad = prioridad
            update_fields.append("prioridad")

        if "respuesta_admin" in payload:
            respuesta_admin = payload["respuesta_admin"]
            if respuesta_admin is not None and not isinstance(respuesta_admin, str):
                return JsonResponse({"success": False, "error": "respuesta_admin debe ser texto o null."}, status=400)
            if respuesta_admin is not None and len(respuesta_admin) > RESPUESTA_ADMIN_MAX_LENGTH:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"La respuesta no puede superar {RESPUESTA_ADMIN_MAX_LENGTH} caracteres.",
                    },
                    status=400,
                )
            ticket.respuesta_admin = respuesta_admin
            update_fields.append("respuesta_admin")

        if not update_fields:
            return JsonResponse({"success": False, "error": "No se enviaron campos actualizables."}, status=400)

        ticket.save(update_fields=update_fields)
        return JsonResponse(
            {
                "success": True,
                "ticket_id": ticket.id,
                "nuevo_estado": ticket.estado,
            }
        )


class EliminarTicketView(StaffRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
            ticket_id = ticket.id
            ticket.delete()
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "error": "Ticket no encontrado."}, status=400)
        except Exception as exc:
            return JsonResponse({"success": False, "error": str(exc)}, status=400)

        return JsonResponse({"success": True, "ticket_id": ticket_id})
