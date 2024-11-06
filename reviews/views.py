from django.shortcuts import render, redirect
from core.decorators import handle_exceptions
from .models import Resena
from .forms import ResenaForm

@handle_exceptions
def ver_resenas(request):
    # Obtener todas las reseñas ordenadas por fecha de creación
    resenas = Resena.objects.all().order_by('-fecha')
    
    # Crear una instancia del formulario de reseña
    form = ResenaForm(request.POST or None)
    
    # Procesar el formulario si se envía a través de POST y es válido
    if request.method == 'POST' and form.is_valid():
        resena = form.save(commit=False)
        resena.usuario = request.user
        resena.save()
        return redirect('reviews:ver_resenas') 
    
    # Lista de estrellas para la valoración
    estrellas = list(range(1, 6))
    
    # Renderizar la plantilla con el formulario y las reseñas
    return render(request, 'reviews/ver_resenas.html', {'form': form, 'resenas': resenas, 'estrellas': estrellas})
