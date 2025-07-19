from django.http import HttpResponsePermanentRedirect


class redirectionDomainMiddleware:
    """
    Middleware to redirect requests from the old domain to the new one with a 301.
    """
    OLD_HOST = 'refactorizaci-n-cabigote-barber-production.up.railway.app'
    NEW_HOST = 'cabigotebarbershop.com'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract host without port
        host = request.get_host().split(':')[0]
        if host == self.OLD_HOST:
            # Permanent redirect to new domain, preserving path and querystring
            return HttpResponsePermanentRedirect(
                f"https://{self.NEW_HOST}{request.get_full_path()}"
            )
        return self.get_response(request)
