from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

class ReporteMensual(models.Model):
    mes = models.DateField(default=now, verbose_name=_("Mes"))
    total_citas = models.IntegerField(default=0, verbose_name=_("Total de citas"))
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Ingresos totales"))
    ingresos_proyectados = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Ingresos proyectados"))
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name=_("Creado el"))

    def __str__(self):
        return f"Reporte para {self.mes.strftime('%B %Y')}"

class ReporteDiario(models.Model):
    dia = models.DateField(default=now, verbose_name=_("Día"))
    total_citas = models.IntegerField(default=0, verbose_name=_("Total de citas"))
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Ingresos totales"))
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name=_("Creado el"))

    def __str__(self):
        return f"Reporte para {self.dia.strftime('%d/%m/%Y')}"