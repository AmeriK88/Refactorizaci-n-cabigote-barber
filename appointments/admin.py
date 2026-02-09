"""
Custom Admin for the *appointments* app.

Includes:
    • Appointment changelist with quick actions and admin-only extras.
    • 12-month stats chart (Matplotlib) moved to service layer,
      and a JSON endpoint suitable for Chart.js.

© 2024-2025  José Félix Gordo Castaño — Educational, non-commercial use only.
"""

from datetime import timedelta

from django.contrib import admin
from django.db.models.functions import ExtractYear
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import BloqueoHora, Cita, FechaBloqueada
from .services.admin_stats import (
    count_appointments_by_month,
    render_monthly_chart_png_base64,
)


# ────────────────────────────────────────────────────────────────────────────────
# SIMPLE LIST FILTER: "Today / Tomorrow"
# Shows a visible filter chip and can be triggered via querystring (?hoy=1)
# ────────────────────────────────────────────────────────────────────────────────
class TodayFilter(admin.SimpleListFilter):
    title = "Hoy"
    parameter_name = "hoy"

    def lookups(self, request, model_admin):
        return (("1", "Hoy"),)

    def queryset(self, request, queryset):
        if self.value() == "1":
            now = timezone.localtime()
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            return queryset.filter(fecha__gte=start, fecha__lt=end)
        return queryset


class TomorrowFilter(admin.SimpleListFilter):
    title = "Mañana"
    parameter_name = "manana"

    def lookups(self, request, model_admin):
        return (("1", "Mañana"),)

    def queryset(self, request, queryset):
        if self.value() == "1":
            now = timezone.localtime()
            start = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end = start + timedelta(days=1)
            return queryset.filter(fecha__gte=start, fecha__lt=end)
        return queryset


# ────────────────────────────────────────────────────────────────────────────────
# FILTER: "Año" (dynamic list of years with appointments, no hardcoding)
# Uses the admin queryset (respects permissions/search if you later add them).
# ────────────────────────────────────────────────────────────────────────────────
class YearFilter(admin.SimpleListFilter):
    title = "Año"
    parameter_name = "year"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        years = (
            qs.annotate(y=ExtractYear("fecha"))
            .values_list("y", flat=True)
            .distinct()
            .order_by("-y")
        )
        return [(str(y), str(y)) for y in years if y is not None]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(fecha__year=int(self.value()))
        return queryset


# ────────────────────────────────────────────────────────────────────────────────
# CITA ADMIN
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """Appointment management + stats chart (clean admin)."""

    list_display = (
        "usuario",
        "servicio",
        "fecha",
        "hora",
        "comentario_corto",
        "vista_icono",
        "ver_grafico_link",
    )
    search_fields = ("usuario__username", "servicio__nombre", "fecha")
    list_filter = (YearFilter, "servicio", TodayFilter, TomorrowFilter)
    ordering = ("-fecha",)
    list_per_page = 20

    actions = ["marcar_como_vistas"]

    # ✅ Default: show current year only (unless user already filtered)
    def changelist_view(self, request, extra_context=None):
        if "year" not in request.GET and not request.GET.get("_changelist_filters"):
            params = request.GET.copy()
            params["year"] = str(timezone.localtime().year)
            request.GET = params
            request.META["QUERY_STRING"] = params.urlencode()
        return super().changelist_view(request, extra_context=extra_context)

    def marcar_como_vistas(self, request, queryset):
        updated = queryset.update(vista=True)
        self.message_user(request, f"{updated} appointment(s) marked as viewed.")
    marcar_como_vistas.short_description = "Marcar como vistas"

    # -------- HELPERS (list_display) --------
    def comentario_corto(self, obj):
        """Truncate long comments with a tooltip."""
        text = obj.comentario or ""
        if len(text) > 50:
            return format_html('<span title="{}">{}…</span>', text, text[:50])
        return text
    comentario_corto.short_description = "Comentario"

    def vista_icono(self, obj):
        """Visual boolean for 'vista'."""
        return "✔️" if obj.vista else "❌"
    vista_icono.short_description = "Vista"

    def ver_grafico_link(self, obj):
        """Per-row link to the chart page (convenience)."""
        url = reverse("admin:cita_dashboard")
        return format_html('<a class="btn-admin-action" href="{}">📊 Dashboard</a>', url)
    ver_grafico_link.short_description = "Gráfico"

    # -------- SHORTCUTS: "Today / Tomorrow" redirect --------
    def citas_hoy_redirect(self, request):
        changelist_url = reverse("admin:appointments_cita_changelist")
        return redirect(f"{changelist_url}?hoy=1")

    def citas_manana_redirect(self, request):
        changelist_url = reverse("admin:appointments_cita_changelist")
        return redirect(f"{changelist_url}?manana=1")

    def dashboard_citas(self, request):
        return render(request, "admin/dashboard_citas.html", {})

    # -------- EXTRA ADMIN URLs --------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "dashboard/",
                self.admin_site.admin_view(self.dashboard_citas),
                name="cita_dashboard",
            ),
            path(
                "graficar/",
                self.admin_site.admin_view(self.graficar_citas),
                name="cita_graph",
            ),
            path(
                "graficar/data/",
                self.admin_site.admin_view(self.graficar_citas_data),
                name="cita_graph_data",
            ),
            path(
                "hoy/",
                self.admin_site.admin_view(self.citas_hoy_redirect),
                name="appointments_cita_changelist_hoy",
            ),
            path(
                "mañana/",
                self.admin_site.admin_view(self.citas_manana_redirect),
                name="appointments_cita_changelist_manana",
            ),
        ]
        return custom + urls

    # -------- Admin views (HTML + JSON) --------
    def graficar_citas(self, request):
        """Render a template with the base64-embedded chart."""
        context = {"grafico": render_monthly_chart_png_base64(months_back=12)}
        return render(request, "admin/grafico_citas.html", context)

    def graficar_citas_data(self, request):
        """Return JSON with labels/counts for Chart.js."""
        labels, counts = count_appointments_by_month(months_back=12)
        return JsonResponse({"labels": labels, "counts": counts})

    class Media:
        css = {"all": ("admin/css/adminDashboard.css",)}


# ────────────────────────────────────────────────────────────────────────────────
# FECHA BLOQUEADA ADMIN
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(FechaBloqueada)
class FechaBloqueadaAdmin(admin.ModelAdmin):
    """Block whole dates (no appointments allowed)."""

    list_display = ("fecha", "razon", "tiene_bloqueos", "ver_bloqueos_link")
    search_fields = ("fecha", "razon")
    list_filter = ("fecha",)

    def tiene_bloqueos(self, obj):
        """True if the date has hour-range blocks registered."""
        return BloqueoHora.objects.filter(fecha=obj.fecha).exists()
    tiene_bloqueos.boolean = True
    tiene_bloqueos.short_description = "Tiene bloqueos"

    def ver_bloqueos_link(self, obj):
        """Link to the hour blocks filtered by the same date."""
        url = (
            reverse("admin:appointments_bloqueohora_changelist")
            + f"?fecha__exact={obj.fecha.isoformat()}"
        )
        return format_html(
            '<a class="btn-admin-action" href="{}">Ver franjas horarias</a>',
            url,
        )
    ver_bloqueos_link.short_description = "Franjas horarias"

    class Media:
        css = {"all": ("admin/css/adminDashboard.css",)}


# ────────────────────────────────────────────────────────────────────────────────
# BLOQUEO HORA ADMIN
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(BloqueoHora)
class BloqueoHoraAdmin(admin.ModelAdmin):
    """Block hour ranges within a specific date."""

    list_display = ("fecha", "hora_inicio", "hora_fin", "razon")
    list_filter = ("fecha",)
    search_fields = ("fecha", "razon")

    class Media:
        css = {"all": ("admin/css/adminDashboard.css",)}
