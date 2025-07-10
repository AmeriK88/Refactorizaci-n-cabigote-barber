from django.db import models

class MensajeEspecial(models.Model):
    titulo = models.CharField(max_length=200, blank=True, null=True)
    contenido = models.TextField()
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.activo:
            # Desactivar otros mensajes activos
            MensajeEspecial.objects.filter(activo=True).exclude(id=self.id).update(activo=False)  # type: ignore[arg-type]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo if self.titulo else f"Mensaje {self.id}" # type: ignore[arg-type]
    
class ContadorVisitas(models.Model):
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Visitas totales: {self.total}"

