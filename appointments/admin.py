from django.contrib import admin
from .models import Cita, FechaBloqueada, BloqueoHora
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from django.urls import path, reverse
from django.shortcuts import render
import seaborn as sns
from django.db.models.functions import TruncMonth

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'fecha', 'hora', 'comentario', 'vista', 'ver_grafico_link')
    search_fields = ('usuario__username', 'servicio__nombre', 'fecha')
    list_filter = ('fecha', 'servicio')
    ordering = ('-fecha',)
    # Limitar a 25 registros por página
    list_per_page = 20

    actions = ['marcar_como_vistas']  # Agrega la acción personalizada

    # Acción para marcar como vistas
    def marcar_como_vistas(self, request, queryset):
        actualizado = queryset.update(vista=True)
        self.message_user(request, f'{actualizado} cita(s) marcada(s) como vista(s).')
    marcar_como_vistas.short_description = "Marcar como vistas"  

    # Muestra un link para acceder al gráfico
    def ver_grafico_link(self, obj):
        return format_html('<a href="{}">Ver Gráfico</a>', reverse('admin:graficar_citas'))
    
    #  Genera el gráfico de citas/obtener datos de citas
    def generar_grafico(self):
        citas_por_mes = Cita.objects.filter(fecha__gte=timezone.now() - timezone.timedelta(days=30)) \
            .annotate(mes=TruncMonth('fecha')) \
            .values('mes') \
            .annotate(total=Count('id'))

        meses = []
        total_citas = []
        for cita in citas_por_mes:
            meses.append(cita['mes'].strftime('%Y-%m'))  
            total_citas.append(cita['total'])

        plt.figure(figsize=(12, 6)) 
        sns.barplot(x=meses, y=total_citas, hue=meses, palette='viridis', dodge=False, legend=False)
        plt.title('Citas por Mes', fontsize=16, fontweight='bold')
        plt.xlabel('Meses', fontsize=12)
        plt.ylabel('Total de Citas', fontsize=12)
        plt.xticks(rotation=45)  
        plt.tight_layout()  

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        plt.close()

        return uri

    # Añade una nueva ruta para la vista del gráfico
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('graficar/', self.admin_site.admin_view(self.graficar_citas), name='graficar_citas'),
        ]
        return custom_urls + urls

    # Vista que renderiza la plantilla con el gráfico de citas
    def graficar_citas(self, request):
        context = {
            'grafico': self.generar_grafico(),
        }
        return render(request, 'admin/grafico_citas.html', context)
    
@admin.register(FechaBloqueada)
class FechaBloqueadaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'razon')
    search_fields = ('fecha', 'razon')
    list_filter = ('fecha',)

@admin.register(BloqueoHora)
class BloqueoHoraAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora_inicio', 'hora_fin', 'razon')
    list_filter = ('fecha',)
    search_fields = ('fecha', 'razon')
