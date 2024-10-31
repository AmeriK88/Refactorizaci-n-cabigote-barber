from core.decorators import handle_exceptions
from django.shortcuts import render, get_object_or_404
from .models import Imagen

# Create your views here.
@handle_exceptions
def ver_imagenes(request):
    imagenes = Imagen.objects.all()
    return render(request, 'media/ver_imagenes.html', {'imagenes': imagenes})

@handle_exceptions
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Imagen, id=producto_id)
    return render(request, 'media/detalle_producto.html', {'producto': producto})