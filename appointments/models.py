# appointments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from services.models import Servicio

class Cita(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
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
        # Ahora puedes usar calcular_reporte aquí
