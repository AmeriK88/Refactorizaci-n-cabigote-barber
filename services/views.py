from django.shortcuts import render
from .models import Servicio

# Services views
def ver_servicios(request):
    servicios = Servicio.objects.all()
    
    return render(request, 'services/servicios.html', {'servicios': servicios})