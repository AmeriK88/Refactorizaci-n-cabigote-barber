"""
Admin personalizado para la app *appointments*.
Incluye:
    • Listado de citas con accesos rápidos y acciones.
    • Gráfico de estadísticas de los últimos 12 meses —sin depender de funciones SQL
      incompatibles— generado con Matplotlib y servible también en formato JSON
      para Chart.js.

© 2024‑2025  José Félix Gordo Castaño — Uso educativo, no comercial.
"""

from collections import defaultdict
import io
import base64

import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from django.contrib import admin
from django.urls import path, reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html
from django.utils.timezone import localtime

from .models import Cita, FechaBloqueada, BloqueoHora


# ────────────────────────────────────────────────────────────────────────────────
# CITA ADMIN
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """Gestión de citas + estadísticas gráficas."""

    # -------- MAIN BOARD --------
    list_display = (
        "usuario",
        "servicio",
        "fecha",
        "hora",
        "comentario_corto",
        "vista_icon",
        "ver_grafico_link",
    )
    search_fields = ("usuario__username", "servicio__nombre", "fecha")
    list_filter = ("fecha", "servicio")
    ordering = ("-fecha",)
    list_per_page = 20

    # -------- ACTIONS --------
    actions = ["marcar_como_vistas"]

    def marcar_como_vistas(self, request, queryset):
        actualizado = queryset.update(vista=True)
        self.message_user(request, f"{actualizado} cita(s) marcadas como vista(s).")

    marcar_como_vistas.short_description = "Marcar como vistas"

    # -------- HELPERS --------
    def comentario_corto(self, obj):
        texto = obj.comentario or ""
        if len(texto) > 50:
            return format_html('<span title="{}">{}…</span>', texto, texto[:50])
        return texto

    comentario_corto.short_description = "Comentario"

    def vista_icon(self, obj):
        return "✔️" if obj.vista else "❌"

    def ver_grafico_link(self, obj):
        url = reverse("admin:cita_graph")
        return format_html('<a class="button btn-admin-action" href="{}">📊 Ver Gráfico</a>', url)

    ver_grafico_link.short_description = "Gráfico"

    # -------- URLs extra --------
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("graficar/", self.admin_site.admin_view(self.graficar_citas), name="cita_graph"),
            path(
                "graficar/data/",
                self.admin_site.admin_view(self.graficar_citas_data),
                name="cita_graph_data",
            ),
        ]
        return custom + urls

    # ------------------------------------------------------------------
    #   STATS 
    # ------------------------------------------------------------------
    def _contar_citas_por_mes(self, meses_atras: int = 12):
        """Devuelve (labels, counts) desde *meses_atras* hasta hoy (incluye futuro)."""
        inicio = timezone.now() - timezone.timedelta(days=30 * meses_atras)

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
            labels, counts = ["Sin datos"], [0]

        return labels, counts

    # -------- Gráfico PNG embebido (Matplotlib) --------
    def generar_grafico(self):
        """Devuelve una cadena data‑URI PNG para incrustar en <img>."""
        labels, counts = self._contar_citas_por_mes()

        plt.figure(figsize=(10, 5))
        plt.bar(labels, counts, color="skyblue")
        plt.xticks(rotation=45)
        plt.title("Citas por mes")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()

        return f"data:image/png;base64,{img_b64}"

    # -------- Vistas admin --------
    def graficar_citas(self, request):
        """Renderiza el template con la imagen en base64."""
        contexto = {"grafico": self.generar_grafico()}
        return render(request, "admin/grafico_citas.html", contexto)

    def graficar_citas_data(self, request):
        """Retorna JSON labels/counts para Chart.js."""
        labels, counts = self._contar_citas_por_mes()
        return JsonResponse({"labels": labels, "counts": counts})

    # -------- Media extra --------
    class Media:
        css = {"all": ("admin/css/adminCSS.css",)}


# ────────────────────────────────────────────────────────────────────────────────
# FECHA BLOQUEADA ADMIN
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(FechaBloqueada)
class FechaBloqueadaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "razon", "tiene_bloqueos", "ver_bloqueos_link")
    search_fields = ("fecha", "razon")
    list_filter = ("fecha",)

    def tiene_bloqueos(self, obj):
        return BloqueoHora.objects.filter(fecha=obj.fecha).exists()

    tiene_bloqueos.boolean = True
    tiene_bloqueos.short_description = "Tiene bloqueos"

    def ver_bloqueos_link(self, obj):
        url = (
            reverse("admin:appointments_bloqueohora_changelist")
            + f"?fecha__exact={obj.fecha.isoformat()}"
        )
        return format_html('<a href="{}">Ver franjas</a>', url)

    ver_bloqueos_link.short_description = "Franjas"

    class Media:
        css = {"all": ("admin/css/adminCSS.css",)}


# ────────────────────────────────────────────────────────────────────────────────
# BLOQUEO HORA ADMIN
# ────────────────────────────────────────────────────────────────────────────────
@admin.register(BloqueoHora)
class BloqueoHoraAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora_inicio", "hora_fin", "razon")
    list_filter = ("fecha",)
    search_fields = ("fecha", "razon")

    class Media:
        css = {"all": ("admin/css/adminCSS.css",)}
