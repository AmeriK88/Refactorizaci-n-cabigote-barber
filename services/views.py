from django.shortcuts import render
from .models import Servicio

# Create your views here.
def ver_servicios(request):
    servicios = Servicio.objects.all()
    
    return render(request, 'services/servicios.html', {'servicios': servicios})