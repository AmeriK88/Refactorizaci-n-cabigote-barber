from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class RedirectionDomainMiddleware:
    """
    Redirige del dominio antiguo al nuevo con 301, preservando path y querystring.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.old_host = getattr(settings, "OLD_HOST", "refactorizaci-n-cabigote-barber-production.up.railway.app")
        self.new_host = getattr(settings, "NEW_HOST", "cabigotebarbershop.com")

    def __call__(self, request):
        # Obtén host sin puerto. Si hay proxy, Django ya respeta X-Forwarded-Host con SECURE_PROXY_SSL_HEADER.
        host = request.get_host().split(':')[0]
        if host == self.old_host:
            scheme = "https"  # fuerza https en redirección definitiva
            return HttpResponsePermanentRedirect(f"{scheme}://{self.new_host}{request.get_full_path()}")
        return self.get_response(request)
