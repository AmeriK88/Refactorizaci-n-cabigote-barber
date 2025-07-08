# appointments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from services.models import Servicio
from django.utils.translation import gettext_lazy as _
from products.models import Imagen

class Cita(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    producto = models.ForeignKey(Imagen, on_delete=models.SET_NULL, blank=True, null=True)
    fecha = models.DateTimeField()
    hora = models.TimeField()
    comentario = models.TextField(blank=True, null=True)
    vista = models.BooleanField(default=False)

    def __str__(self):
        return f'Cita para {self.usuario} el {self.fecha.date()} a las {self.hora}'

    def puede_cancelar(self):
        limite_cancelacion = self.fecha - timezone.timedelta(days=1)
        return timezone.now() < limite_cancelacion

    def some_method_using_report(self):
        from reports.utils import calcular_reporte


class FechaBloqueada(models.Model):
    fecha = models.DateField(unique=True, verbose_name=_("Fecha Bloqueada"))
    razon = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Razón"))

    def __str__(self):
        return f"{self.fecha} - {self.razon if self.razon else _('Sin razón especificada')}"
    
class BloqueoHora(models.Model):
    fecha = models.DateField(verbose_name=_("Fecha Bloqueada (Hora)"))
    hora_inicio = models.TimeField(verbose_name=_("Hora de inicio"))
    hora_fin = models.TimeField(verbose_name=_("Hora de fin"))
    razon = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Razón"))

    def __str__(self):
        return f"{self.fecha} from {self.hora_inicio.strftime('%H:%M')} to {self.hora_fin.strftime('%H:%M')}"

