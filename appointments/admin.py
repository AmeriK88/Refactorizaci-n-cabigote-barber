from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'fecha', 'hora')  # Campos que deseas mostrar
    search_fields = ('usuario__username', 'servicio__nombre')  # Suponiendo que `usuario` es un ForeignKey
