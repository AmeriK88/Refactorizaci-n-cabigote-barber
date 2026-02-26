from django.shortcuts import render
from core.models import ContadorVisitas
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import os
from services.models import Servicio
from django.utils import timezone


def home(request):
    # INCREMENT COUNTER
    contador, _ = ContadorVisitas.objects.get_or_create(pk=1)
    contador.total += 1
    contador.save()
    contador.refresh_from_db()

    # GET SERVICES
    servicios = Servicio.objects.all().order_by('nombre')

    context = {
        'contador_actualizado': contador.total,
        'servicios': servicios,
        'now': timezone.now(),
    }

    response = render(request, 'home.html', context)

    # FORCE NO CACHE.
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


@csrf_exempt
def lanzar_recordatorios(request):
    # PROTECT WITH SECRET KEY
    if request.GET.get('secret') != os.environ.get('CRON_SECRET_KEY'):
        return JsonResponse({'error': 'No autorizado'}, status=401)

    # CUSTOM COMMAND
    resultado = subprocess.run(['python', 'manage.py', 'enviar_recordatorios'], capture_output=True, text=True)

    return JsonResponse({
        'status': 'ok',
        'salida': resultado.stdout,
        'errores': resultado.stderr
    })