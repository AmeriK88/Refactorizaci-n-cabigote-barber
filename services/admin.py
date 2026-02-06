from django.contrib import admin
from django.utils.html import format_html
from .models import Servicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'imagen_preview', 'duracion')
    search_fields  = ('nombre',)
    ordering       = ('nombre',)
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        if obj.imagen:
            # la miniatura es un <img> con clases CSS para redondear, sombra y hover,
            # y envuelto en un <a> que abre la imagen completa en una pestaña nueva
            return format_html(
                '<a href="{0}" target="_blank">'
                '  <img src="{0}" class="admin-thumb" alt="{1}" />'
                '</a>',
                obj.imagen.url,
                obj.nombre
            )
        return format_html('<span class="text-muted">(sin imagen)</span>')
    imagen_preview.short_description = 'Imagen'

    class Media:
        css = {
            'all': ('admin/css/adminCSS.css',)
        }


# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.