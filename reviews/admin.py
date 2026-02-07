from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Resena


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    """
    Admin mejorado para las reseñas de servicios.
    """
    list_display = (
        'usuario', 'servicio',
        'puntuacion_icon',     # ★★★★☆
        'snippet',             # vista previa del comentario
        'fecha',
    )
    list_select_related = ('usuario', 'servicio')
    list_per_page = 40

    # filtros, orden, búsqueda
    list_filter   = ('puntuacion', 'servicio')
    ordering      = ('-fecha',)
    search_fields = ('texto', 'usuario__username', 'servicio__nombre')

    # ───────── helpers de columnas ──────────
    @admin.display(description='Comentario')
    def snippet(self, obj):
        texto = (obj.texto[:80] + '…') if len(obj.texto) > 80 else obj.texto
        url   = reverse('admin:reviews_resena_change', args=[obj.pk])
        return format_html('<span title="{}">{}</span> <a href="{}">→ ver</a>',
                           obj.texto, texto, url)

    @admin.display(description='Puntuación', ordering='puntuacion')
    def puntuacion_icon(self, obj):
        # 5 estrellas doradas, las vacías en gris
        estrellas = ''.join(
            '⭐' if i < obj.puntuacion else '☆' for i in range(5)
        )
        color = '#ffc107' if obj.puntuacion else '#dc3545'
        return mark_safe(f'<span style="color:{color}; font-size:18px">{estrellas}</span>')

    # ───────── CSS extra para el listado ─────
    class Media:
        css = {
            'all': ('admin/css/adminDashboard.css',),  
        }
