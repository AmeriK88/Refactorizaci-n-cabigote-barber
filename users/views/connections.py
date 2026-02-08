from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from core.web.decorators import handle_exceptions

@login_required
@handle_exceptions
def connections_view(request):
    return redirect("socialaccount_connections")
