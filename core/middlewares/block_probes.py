import re, time
from dataclasses import dataclass
from typing import List
from django.core.cache import cache
from django.http import HttpResponseNotFound, HttpResponse

BAN_MINUTES = 60    
WINDOW_SECONDS = 300 
THRESHOLD = 10 

@dataclass(frozen=True)
class ProbeRule:
    name: str
    regex: str

PROBE_RULES: List[ProbeRule] = [
    ProbeRule("wordpress_php_files",      r"\.php($|\?)"),
    ProbeRule("wordpress_prefix_wp_dash", r"^/wp-"),
    ProbeRule("wordpress_folder_wp",      r"^/wp/"),
    ProbeRule("xmlrpc_endpoint",          r"/xmlrpc\.php$"),
    ProbeRule("wlw_manifest",             r"/wlwmanifest\.xml$"),
    ProbeRule("admin_php",                r"^/admin\.php$"),
    ProbeRule("public_html",              r"^/public_html$"),
    ProbeRule("random_r_php",             r"^/r\.php$"),
    ProbeRule("random_tiny_php",          r"^/tiny\.php$"),
    ProbeRule("random_chosen_php",        r"^/chosen\.php$"),
    # Variantes típicas
    ProbeRule("double_slash_wp_includes", r"^//wp-includes/"),
    ProbeRule("double_slash_xmlrpc",      r"^//xmlrpc\.php$"),
    ProbeRule("wp_id3_license",           r"/wp-includes/ID3/license\.txt$"),
]

_COMPILED = [(rule.name, re.compile(rule.regex, re.IGNORECASE)) for rule in PROBE_RULES]

def path_looks_suspicious(path: str) -> bool:
    return any(p.search(path) for _, p in _COMPILED)

def _key(ip: str, suffix: str) -> str:
    return f"probes:{ip}:{suffix}"

class BlockProbesMiddleware:
    """
    1) Si la IP está baneada => 404 inmediato.
    2) Si la ruta huele a probe => incrementa contador en ventana y, si supera umbral, banea IP.
    3) En cualquier otro caso pasa la request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "unknown")
        now = int(time.time())

        # 1) ¿Baneado?
        if cache.get(_key(ip, "ban")):
            return HttpResponseNotFound()

        path = request.path or "/"

        # 2) ¿Huele a probe?
        if path_looks_suspicious(path):
            window_key = _key(ip, f"w:{now // WINDOW_SECONDS}")
            count = cache.incr(window_key) if cache.get(window_key) else (cache.set(window_key, 1, WINDOW_SECONDS) or 1)
            if count >= THRESHOLD:
                cache.set(_key(ip, "ban"), 1, BAN_MINUTES * 60)
            return HttpResponseNotFound()

        return self.get_response(request)
