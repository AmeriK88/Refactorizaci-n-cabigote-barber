from decimal import Decimal
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

class ReporteMensual(models.Model):
    mes = models.DateField(default=now, verbose_name=_("Mes"))
    total_citas = models.IntegerField(default=0, verbose_name=_("Total de citas"))
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"),
                                           verbose_name=_("Ingresos totales"))
    ingresos_proyectados = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"),
                                               verbose_name=_("Ingresos proyectados"))
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name=_("Creado el"))

    def save(self, *args, **kwargs):
        # Normaliza al primer día del mes para garantizar unicidad por mes
        if self.mes:
            self.mes = self.mes.replace(day=1)
        super().save(*args, **kwargs)

    def __str__(self):
        # Ej.: "Reporte para March 2025"
        return f"Reporte para {self.mes.strftime('%B %Y')}"

    class Meta:
        verbose_name = _("Reporte mensual")
        verbose_name_plural = _("Reportes mensuales")
        ordering = ("-mes",)  # últimos meses primero
        constraints = [
            models.UniqueConstraint(fields=["mes"], name="uniq_reportemensual_mes"),
        ]
        indexes = [
            models.Index(fields=["mes"], name="idx_reportemensual_mes"),
            models.Index(fields=["creado_el"], name="idx_reportemensual_creado"),
        ]


class ReporteDiario(models.Model):
    dia = models.DateField(default=now, verbose_name=_("Día"))
    total_citas = models.IntegerField(default=0, verbose_name=_("Total de citas"))
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"),
                                           verbose_name=_("Ingresos totales"))
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name=_("Creado el"))

    def __str__(self):
        # Ej.: "Reporte para 31/03/2025"
        return f"Reporte para {self.dia.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = _("Reporte diario")
        verbose_name_plural = _("Reportes diarios")
        ordering = ("-dia",)  # últimos días primero
        constraints = [
            models.UniqueConstraint(fields=["dia"], name="uniq_reportediario_dia"),
        ]
        indexes = [
            models.Index(fields=["dia"], name="idx_reportediario_dia"),
            models.Index(fields=["creado_el"], name="idx_reportediario_creado"),
        ]
