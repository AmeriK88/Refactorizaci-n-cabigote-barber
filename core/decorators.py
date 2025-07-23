from functools import wraps
from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import PermissionDenied
import logging

import traceback

def handle_exceptions(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Http404:
            return render(request, 'errors/404.html', status=404)
        except PermissionDenied:
            return render(request, 'errors/403.html', status=403)
        except Exception as e:
            logger = logging.getLogger(__name__)
            # PRINT LOGS
            logger.error("Error inesperado en %s:\n%s", view_func.__name__, traceback.format_exc())
            return render(request, 'errors/500.html', status=500)
    return _wrapped_view

