from django.contrib import admin
from .models import MensajeEspecial, ContadorVisitas


@admin.register(MensajeEspecial)
class MensajeEspecialAdmin(admin.ModelAdmin):
    """
    Listado simple con icono de estado + soporte para banner Lottie.
    """
    list_display = ("titulo", "activo_icon", "lottie_icon", "fecha_inicio", "fecha_fin")
    list_filter = ("activo", "show_lottie")
    search_fields = ("titulo",)

    fieldsets = (
        ("Contenido", {
            "fields": ("titulo", "contenido")
        }),
        ("Estado y fechas", {
            "fields": ("activo", "fecha_inicio", "fecha_fin")
        }),
        ("Animación (Lottie)", {
            "fields": ("show_lottie", "lottie_file"),
            "description": "Ej: lottie/vacation.json (ruta dentro de /static/)"
        }),
    )

    @admin.display(description="Activo", ordering="activo")
    def activo_icon(self, obj):
        return "✔️" if obj.activo else "❌"

    @admin.display(description="Lottie")
    def lottie_icon(self, obj):
        return "🎞️" if obj.show_lottie else "—"

    class Media:
        css = {"all": ("admin/css/adminDashboard.css",)}


@admin.register(ContadorVisitas)
class ContadorVisitasAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("admin/css/adminDashboard.css",)}
