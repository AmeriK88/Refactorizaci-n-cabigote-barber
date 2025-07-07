from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, DateField
from django.utils import timezone
from django.db.models.functions import TruncMonth

from .models import Cita, FechaBloqueada, BloqueoHora

# Configuración para usar Matplotlib sin UI
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display    = ('usuario', 'servicio', 'fecha', 'hora',
                       'comentario_corto', 'vista_icon', 'ver_grafico_link')
    search_fields   = ('usuario__username', 'servicio__nombre', 'fecha')
    list_filter     = ('fecha', 'servicio')
    ordering        = ('-fecha',)
    list_per_page   = 20
    actions         = ['marcar_como_vistas']

    def marcar_como_vistas(self, request, queryset):
        actualizado = queryset.update(vista=True)
        self.message_user(request, f'{actualizado} cita(s) marcadas como vista(s).')
    marcar_como_vistas.short_description = "Marcar como vistas"

    def comentario_corto(self, obj):
        texto = obj.comentario or ""
        if len(texto) > 50:
            return format_html('<span title="{}">{}…</span>', texto, texto[:50])
        return texto
    comentario_corto.short_description = 'Comentario'

    def vista_icon(self, obj):
        return '✔️' if obj.vista else '❌'

    def ver_grafico_link(self, obj):
        url = reverse('admin:cita_graph')
        return format_html('<a class="button ver-grafico" href="{}">📊 Ver Gráfico</a>', url)
    ver_grafico_link.short_description = 'Gráfico'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('graficar/', self.admin_site.admin_view(self.graficar_citas), name='cita_graph'),
            path('graficar/data/', self.admin_site.admin_view(self.graficar_citas_data), name='cita_graph_data'),
        ]
        return custom + urls

    def generar_grafico(self):
        """
        Crea un gráfico de barras con el número de citas en los últimos 6 meses.
        Devuelve un URI base64 para incrustar como <img>.
        """
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        qs = (
            Cita.objects.filter(fecha__gte=six_months_ago)
                  .annotate(mes=TruncMonth('fecha', output_field=DateField()))
                  .values('mes')
                  .annotate(count=Count('id'))
                  .order_by('mes')
        )
        meses = [item['mes'].strftime('%Y-%m') for item in qs]
        totales = [item['count'] for item in qs]

        # Generar gráfico
        plt.figure(figsize=(10, 5))
        plt.bar(meses, totales, color='skyblue')
        plt.xticks(rotation=45)
        plt.title('Citas en los últimos 6 meses')
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return f'data:image/png;base64,{img_b64}'

    def graficar_citas(self, request):
        """
        Vista que renderiza el template con el gráfico incrustado como <img>.
        """
        context = {'grafico': self.generar_grafico()}
        return render(request, 'admin/grafico_citas.html', context)

    def graficar_citas_data(self, request):
        """
        Endpoint JSON para Chart.js (si se prefiere usar JS en lugar de img).
        """
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        qs = (
            Cita.objects.filter(fecha__gte=six_months_ago)
                  .annotate(mes=TruncMonth('fecha', output_field=DateField()))
                  .values('mes')
                  .annotate(count=Count('id'))
                  .order_by('mes')
        )
        data = {
            'labels': [item['mes'].strftime('%Y-%m') for item in qs],
            'counts': [item['count'] for item in qs],
        }
        return JsonResponse(data)

    class Media:
        css = {
            'all': ('admin/css/adminCSS.css',)
        }

@admin.register(FechaBloqueada)
class FechaBloqueadaAdmin(admin.ModelAdmin):
    list_display   = ('fecha', 'razon', 'tiene_bloqueos', 'ver_bloqueos_link')
    search_fields  = ('fecha', 'razon')
    list_filter    = ('fecha',)

    def tiene_bloqueos(self, obj):
        return BloqueoHora.objects.filter(fecha=obj.fecha).exists()
    tiene_bloqueos.boolean = True
    tiene_bloqueos.short_description = 'Tiene bloqueos'

    def ver_bloqueos_link(self, obj):
        url = (
            reverse('admin:appointments_bloqueohora_changelist')
            + f'?fecha__exact={obj.fecha.isoformat()}'
        )
        return format_html('<a href="{}">Ver franjas</a>', url)
    ver_bloqueos_link.short_description = 'Franjas'

    class Media:
        css = {
            'all': ('admin/css/adminCSS.css',)
        }

@admin.register(BloqueoHora)
class BloqueoHoraAdmin(admin.ModelAdmin):
    list_display   = ('fecha', 'hora_inicio', 'hora_fin', 'razon')
    list_filter    = ('fecha',)
    search_fields  = ('fecha', 'razon')

    class Media:
        css = {
            'all': ('admin/css/adminCSS.css',)
        }
