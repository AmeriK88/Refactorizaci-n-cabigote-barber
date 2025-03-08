from django.shortcuts import render
from core.models import ContadorVisitas

def home(request):
    # Incrementar el contador
    contador, _ = ContadorVisitas.objects.get_or_create(pk=1)
    contador.total += 1
    contador.save()

    contador.refresh_from_db()

    # Renderizar la plantilla
    response = render(request, 'home.html', {'contador_actualizado': contador.total})

    # Forzar cabeceras para que el navegador y proxies no guarden en caché
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response
