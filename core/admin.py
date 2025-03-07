from django.contrib import admin
from .models import MensajeEspecial, ContadorVisitas

@admin.register(MensajeEspecial)
class MensajeEspecialAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activo', 'fecha_inicio', 'fecha_fin')
    list_filter = ('activo',)

@admin.register(ContadorVisitas)
class ContadorVisitasAdmin(admin.ModelAdmin):
    pass
