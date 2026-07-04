from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.utils import timezone

import subprocess
import os

from core.models import ContadorVisitas
from services.models import Servicio


def home(request):
    # Crear el contador si no existe
    ContadorVisitas.objects.get_or_create(pk=1, defaults={"total": 0})

    # Incrementar solo una vez por sesión
    if not request.session.get("home_counter_counted"):
        ContadorVisitas.objects.filter(pk=1).update(total=F("total") + 1)
        request.session["home_counter_counted"] = True

    # Obtener el valor actualizado
    contador_total = ContadorVisitas.objects.only("total").get(pk=1).total

    # Obtener servicios
    servicios = Servicio.objects.all().order_by("nombre")

    context = {
        "contador_actualizado": contador_total,
        "servicios": servicios,
        "now": timezone.now(),
    }

    response = render(request, "home.html", context)

    # Evitar caché
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


@csrf_exempt
def lanzar_recordatorios(request):
    # Proteger con clave secreta
    if request.GET.get("secret") != os.environ.get("CRON_SECRET_KEY"):
        return JsonResponse({"error": "No autorizado"}, status=401)

    resultado = subprocess.run(
        ["python", "manage.py", "enviar_recordatorios"],
        capture_output=True,
        text=True,
    )

    return JsonResponse({
        "status": "ok",
        "salida": resultado.stdout,
        "errores": resultado.stderr,
    })


def custom_404_view(request, exception):
    return render(request, "errors/404.html", status=404)