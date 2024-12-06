from django.contrib import admin
from django.utils.html import format_html
from .models import Imagen

class ImagenAdmin(admin.ModelAdmin):
    # Mostrar todos los campos
    list_display = ('titulo', 'precio', 'mostrar_imagen', 'descripcion')  
    search_fields = ('titulo',)
    ordering = ('titulo',)

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.imagen.url)
        return "No hay imagen"
    
     # Nombre de la columna en el admin
    mostrar_imagen.short_description = 'Imagen' 

admin.site.register(Imagen, ImagenAdmin)
