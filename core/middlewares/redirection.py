from django.http import HttpResponsePermanentRedirect
from django.conf import settings


class RedirectionDomainMiddleware:
    """
    Redirect legacy Railway domain and www subdomain
    to the canonical domain.

    Preserves path and query string.
    Returns HTTP 301.
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
            return HttpResponsePermanentRedirect(
                f"https://{self.new_host}{request.get_full_path()}"
            )

        return self.get_response(request)