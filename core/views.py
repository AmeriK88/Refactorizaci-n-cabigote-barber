from django.shortcuts import render
from core.models import ContadorVisitas 

def home(request):
    contador, _ = ContadorVisitas.objects.get_or_create(pk=1)
    contador.total += 1
    contador.save()

    # No pasas nada de 'contador' al template
    return render(request, 'home.html')

