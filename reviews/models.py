from django.db import models
from django.conf import settings
from django.utils import timezone
from services.models import Servicio  

class Resena(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    texto = models.TextField()  
    fecha = models.DateTimeField(default=timezone.now)
    puntuacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1) 

    def __str__(self):
        return f"Reseña de {self.usuario.username} - {self.servicio.nombre} - {self.puntuacion} estrellas"
