from django.contrib import admin
from django.utils.html import format_html
from .models import MensajeEspecial, ContadorVisitas


@admin.register(MensajeEspecial)
class MensajeEspecialAdmin(admin.ModelAdmin):
    """
    Listado simple con icono de estado.
    """
    list_display = ('titulo', 'activo_icon', 'fecha_inicio', 'fecha_fin')
    list_filter  = ('activo',)
    search_fields = ('titulo',)

    @admin.display(description='Activo', ordering='activo')
    def activo_icon(self, obj):
        return '✔️' if obj.activo else '❌'

    class Media:
        css = {'all': ('admin/css/adminCSS.css',)}


@admin.register(ContadorVisitas)
class ContadorVisitasAdmin(admin.ModelAdmin):
    pass

    class Media:
        css = {'all': ('admin/css/adminCSS.css',)}
