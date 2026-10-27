
from django.conf import settings
from django.http import (
    HttpResponsePermanentRedirect,
    HttpResponse,
)


class RedirectionDomainMiddleware:
    """
    Redirige dominios antiguos y www al dominio canónico.

    - GET y HEAD: redirección permanente 301.
    - POST, PUT, PATCH y DELETE: no redirige automáticamente.
    - Conserva la ruta y los parámetros de consulta.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        self.old_host = getattr(
            settings,
            "OLD_HOST",
            "refactorizaci-n-cabigote-barber-production.up.railway.app",
        )

        self.new_host = getattr(
            settings,
            "NEW_HOST",
            "cabigotebarbershop.com",
        )

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()

        redirect_hosts = {
            self.old_host.lower(),
            f"www.{self.new_host.lower()}",
        }

        if host in redirect_hosts:
            if request.method not in ("GET", "HEAD"):
                return HttpResponse(
                    "Utiliza el dominio canónico para enviar formularios.",
                    status=400,
                )

            return HttpResponsePermanentRedirect(
                f"https://{self.new_host}{request.get_full_path()}"
            )

        return self.get_response(request)
