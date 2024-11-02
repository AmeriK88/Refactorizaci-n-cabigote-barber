# reviews/admin.py
from django.contrib import admin
from .models import Resena

class ResenaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'puntuacion', 'fecha')
    search_fields = ('usuario__username', 'servicio__nombre')
    ordering = ('-fecha',)
    list_filter = ('puntuacion', 'servicio')
    

admin.site.register(Resena, ResenaAdmin)
