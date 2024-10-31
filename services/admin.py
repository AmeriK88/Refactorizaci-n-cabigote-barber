from django.contrib import admin
from django.utils.html import format_html
from .models import Servicio

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'mostrar_imagen')  # Mostrar todos los campos
    search_fields = ('nombre',)
    ordering = ('nombre',)

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.imagen.url)
        return "No hay imagen"

    mostrar_imagen.short_description = 'Imagen'  

admin.site.register(Servicio, ServicioAdmin)
