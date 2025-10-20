# core/middlewares/block_probes.py
import re
from dataclasses import dataclass
from typing import List
from django.http import HttpResponseNotFound

@dataclass(frozen=True)
class ProbeRule:
    """Describe un patrón de URL sospechosa."""
    name: str
    regex: str

# Reglas explícitas y fáciles de leer
PROBE_RULES: List[ProbeRule] = [
    ProbeRule(name="wordpress_php_files",      regex=r"\.php($|\?)"),
    ProbeRule(name="wordpress_prefix_wp_dash", regex=r"^/wp-"),
    ProbeRule(name="wordpress_folder_wp",      regex=r"^/wp/"),
    ProbeRule(name="xmlrpc_endpoint",          regex=r"/xmlrpc\.php$"),
    ProbeRule(name="wlw_manifest",             regex=r"/wlwmanifest\.xml$"),
    ProbeRule(name="admin_php",                regex=r"^/admin\.php$"),
    ProbeRule(name="public_html",              regex=r"^/public_html$"),
    ProbeRule(name="random_r_php",             regex=r"^/r\.php$"),
    ProbeRule(name="random_tiny_php",          regex=r"^/tiny\.php$"),
    ProbeRule(name="random_chosen_php",        regex=r"^/chosen\.php$"),
    # Variantes típicas
    ProbeRule(name="double_slash_wp_includes", regex=r"^//wp-includes/"),
    ProbeRule(name="double_slash_xmlrpc",      regex=r"^//xmlrpc\.php$"),
    ProbeRule(name="wp_id3_license",           regex=r"/wp-includes/ID3/license\.txt$"),
]

_COMPILED = [(rule.name, re.compile(rule.regex, re.IGNORECASE)) for rule in PROBE_RULES]

def path_looks_suspicious(path: str) -> bool:
    """Devuelve True si el path coincide con algún patrón sospechoso."""
    for rule_name, pattern in _COMPILED:
        if pattern.search(path):
            return True
    return False

class BlockProbesMiddleware:
    """
    Corta de raíz requests a rutas probadas por bots (WordPress, xmlrpc, *.php, etc.)
    Devolvemos 404 para no dar pistas al atacante.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if path_looks_suspicious(request.path):
            return HttpResponseNotFound()
        return self.get_response(request)
