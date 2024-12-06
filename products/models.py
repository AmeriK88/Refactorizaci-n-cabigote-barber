from django.db import models

# Create your models here.
class Imagen(models.Model):
    titulo = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.titulo