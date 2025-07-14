from django.shortcuts import render
from core.models import ContadorVisitas
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
from services.models import Servicio


def home(request):
    # Incrementar el contador
    contador, _ = ContadorVisitas.objects.get_or_create(pk=1)
    contador.total += 1
    contador.save()

    contador.refresh_from_db()

    # Obtener servicios para mostrar en home
    servicios = Servicio.objects.all().order_by('nombre')

    # Contexto para la plantilla
    context = {
        'contador_actualizado': contador.total,
        'servicios': servicios,
    }

    # Renderizar la plantilla
    response = render(request, 'home.html', context)

    # Forzar cabeceras para que el navegador y proxies no guarden en caché
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


@csrf_exempt
def lanzar_recordatorios(request):
    # Proteger con clave secreta (usada en la URL)
    if request.GET.get('secret') != os.environ.get('CRON_SECRET_KEY'):
        return JsonResponse({'error': 'No autorizado'}, status=401)

    # Ejecutar el comando personalizado
    resultado = subprocess.run(['python', 'manage.py', 'enviar_recordatorios'], capture_output=True, text=True)

    return JsonResponse({
        'status': 'ok',
        'salida': resultado.stdout,
        'errores': resultado.stderr
    })