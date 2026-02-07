from django.contrib import admin
from django.utils.html import format_html
from .models import Imagen

@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display   = ('titulo', 'precio_formateado', 'imagen_preview', 'descripcion')
    search_fields  = ('titulo',)
    ordering       = ('titulo',)
    readonly_fields = ('imagen_preview',)

    def precio_formateado(self, obj):
        return f"€{obj.precio:.2f}"
    precio_formateado.short_description = 'Precio'

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<a href="{0}" target="_blank">'
                '  <img src="{0}" class="admin-thumb" alt="{1}" />'
                '</a>',
                obj.imagen.url,
                obj.titulo
            )
        return format_html('<span class="text-muted">(no image)</span>')
    imagen_preview.short_description = 'Imagen'

    class Media:
        css = {
            'all': ('admin/css/adminDashboard.css',)
        }
