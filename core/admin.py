from django.contrib import admin
from .models import MensajeEspecial

@admin.register(MensajeEspecial)
class MensajeEspecialAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activo', 'fecha_inicio', 'fecha_fin')
    list_filter = ('activo',)
