"""
Custom Admin for the *appointments* app.

Includes:
    • Appointment changelist with quick actions and admin-only extras.
    • 12-month stats chart (Matplotlib) without DB-specific SQL functions,
      and a JSON endpoint suitable for Chart.js.

© 2024-2025  José Félix Gordo Castaño — Educational, non-commercial use only.
"""

from collections import defaultdict
import io
import base64

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environments
import matplotlib.pyplot as plt

from datetime import timedelta

from django.contrib import admin
from django.urls import path, reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.html import format_html
from django.utils.timezone import localtime

from .models import Cita, FechaBloqueada, BloqueoHora


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
            # Filter by local-day range [00:00, 24:00) — DST-safe
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
            start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            return queryset.filter(fecha__gte=start, fecha__lt=end)
        return queryset


# ────────────────────────────────────────────────────────────────────────────────
# CITA ADMIN
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """Appointment management + stats chart."""

    # -------- MAIN BOARD --------
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
    list_filter = ("fecha", "servicio", TodayFilter, TomorrowFilter)
    ordering = ("-fecha",)
    list_per_page = 20

    # -------- ACTIONS --------
    actions = ["marcar_como_vistas"]

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

    def ver_grafico_link(self, obj):
        """Per-row link to the chart page (convenience)."""
        url = reverse("admin:cita_graph")
        return format_html('<a class="button btn-admin-action" href="{}">📊 Gráfico</a>', url)
    ver_grafico_link.short_description = "Gráfico"

    # -------- SHORTCUT: "Today" redirect --------
    def citas_hoy_redirect(self, request):
        """
        Redirect to the Cita changelist applying the 'Hoy' filter.
        We use the SimpleListFilter via querystring (?hoy=1) so the filter chip is visible.
        """
        changelist_url = reverse("admin:appointments_cita_changelist")
        return redirect(f"{changelist_url}?hoy=1")
    
    def citas_manana_redirect(self, request):
        changelist_url = reverse("admin:appointments_cita_changelist")
        return redirect(f"{changelist_url}?manana=1")

    # -------- EXTRA ADMIN URLs --------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("graficar/", self.admin_site.admin_view(self.graficar_citas), name="cita_graph"),
            path("graficar/data/", self.admin_site.admin_view(self.graficar_citas_data), name="cita_graph_data"),
            # Shortcut to show only today's appointments
            path("hoy/", self.admin_site.admin_view(self.citas_hoy_redirect), name="appointments_cita_changelist_hoy"),
            path("mañana/", self.admin_site.admin_view(self.citas_manana_redirect), name="appointments_cita_changelist_manana"),
        ]
        return custom + urls

    # ------------------------------------------------------------------
    #   STATS: APPOINTMENTS PER MONTH (Matplotlib + JSON)
    # ------------------------------------------------------------------
    def _contar_citas_por_mes(self, meses_atras: int = 12):
        """
        Return (labels, counts) for the last *meses_atras* months up to now.
        Labels are YYYY-MM, counts are total appointments in that month.
        """
        inicio = timezone.now() - timedelta(days=30 * meses_atras)

        fechas = (
            Cita.objects.filter(fecha__gte=inicio, fecha__isnull=False)
            .values_list("fecha", flat=True)
        )

        contador = defaultdict(int)
        for fecha in fechas:
            f_local = localtime(fecha)
            label = f"{f_local.year}-{f_local.month:02d}"
            contador[label] += 1

        labels = sorted(contador.keys())
        counts = [contador[l] for l in labels]

        if not labels:
            labels, counts = ["No data"], [0]

        return labels, counts

    # -------- Embedded PNG chart (Matplotlib) --------
    def generar_grafico(self):
        """Return a data-URI PNG to embed in <img>."""
        labels, counts = self._contar_citas_por_mes()

        plt.figure(figsize=(10, 5))
        plt.bar(labels, counts, color="skyblue")
        plt.xticks(rotation=45)
        plt.title("Citas por mes (últimos 12 meses)")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()

        return f"data:image/png;base64,{img_b64}"

    # -------- Admin views (HTML + JSON) --------
    def graficar_citas(self, request):
        """Render a template with the base64-embedded chart."""
        context = {"grafico": self.generar_grafico()}
        return render(request, "admin/grafico_citas.html", context)

    def graficar_citas_data(self, request):
        """Return JSON with labels/counts for Chart.js."""
        labels, counts = self._contar_citas_por_mes()
        return JsonResponse({"labels": labels, "counts": counts})

    # -------- Extra media (CSS) --------
    class Media:
        css = {"all": ("admin/css/adminCSS.css",)}


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
        return format_html('<a href="{}">Ver franjas horarias</a>', url)
    ver_bloqueos_link.short_description = "Franjas horarias"

    class Media:
        css = {"all": ("admin/css/adminCSS.css",)}


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
        css = {"all": ("admin/css/adminCSS.css",)}
