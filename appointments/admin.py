from django.contrib import admin
from .models import Cita
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from django.urls import path
from django.shortcuts import render
import seaborn as sns
from django.db.models.functions import TruncMonth
from django.urls import reverse  # Importa reverse para generar URLs

class CitaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'fecha', 'hora', 'mostrar_grafico', 'ver_grafico_link', 'estado_vista')  
    search_fields = ('usuario__username', 'servicio__nombre')
    list_filter = ('vista', 'servicio', 'fecha')

    def estado_vista(self, obj):
        """ Devuelve un ícono o texto basado en el estado de vista de la cita. """
        if obj.vista:
            return format_html('<span style="color: green;">Vista</span>')  
        else:
            return format_html('<span style="color: red;">No Vista</span>')  
    estado_vista.short_description = 'Estado'

    def mostrar_grafico(self, obj):
        """ Muestra gráfico en la lista de citas en el admin. """
        return format_html('<img src="{}" style="max-height: 200px; max-width: 100%;" />', self.generar_grafico())

    def ver_grafico_link(self, obj):
        """ Devuelve un enlace que permite ver el gráfico en una página separada. """
        return format_html('<a href="{}">Ver Gráfico</a>', reverse('admin:graficar_citas'))

    def get_grafico_url(self):
        """ Devuelve la URL donde se puede acceder al gráfico. """
        return 'admin/appointments/graficar/'

    def generar_grafico(self):
        """ Genera el gráfico de citas por mes utilizando Seaborn y devuelve una imagen codificada en base64. """
        # Obtener datos de citas agrupados por mes utilizando TruncMonth
        citas_por_mes = Cita.objects.filter(fecha__gte=timezone.now() - timezone.timedelta(days=30)) \
            .annotate(mes=TruncMonth('fecha')) \
            .values('mes') \
            .annotate(total=Count('id'))

        # Preparar datos para el gráfico
        meses = []
        total_citas = []
        for cita in citas_por_mes:
            # Formatear el mes para mostrarlo
            meses.append(cita['mes'].strftime('%Y-%m'))  
            total_citas.append(cita['total'])

        # Configurar gráfico con Seaborn
        plt.figure(figsize=(10, 5)) 
        sns.barplot(x=meses, y=total_citas, hue=meses, palette='viridis', legend=False)
        plt.title('Citas por Mes')
        plt.xlabel('Meses')
        plt.ylabel('Total de Citas')
        
        # Guardar el gráfico en un objeto BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        plt.close()

        return uri

    def get_urls(self):
        """ Añade una nueva ruta para la vista del gráfico. """
        urls = super().get_urls()
        custom_urls = [
            path('graficar/', self.admin_site.admin_view(self.graficar_citas), name='graficar_citas'),
        ]
        return custom_urls + urls

    def graficar_citas(self, request):
        """ Vista que renderiza la plantilla con el gráfico de citas. """
        context = {
            'grafico': self.generar_grafico(),
        }
        return render(request, 'admin/grafico_citas.html', context)

admin.site.register(Cita, CitaAdmin)
