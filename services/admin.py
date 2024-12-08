from django.contrib import admin
from django.utils.html import format_html
from .models import Servicio

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'precio', 'mostrar_imagen') 
    search_fields = ('nombre',)
    ordering = ('nombre',)

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.imagen.url)
        return "No hay imagen"

    mostrar_imagen.short_description = 'Imagen'  

admin.site.register(Servicio, ServicioAdmin)

# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.