import logging
import re
from dataclasses import dataclass
from typing import List
from django.http import HttpResponseNotFound

@dataclass(frozen=True)
class ProbeRule:
    """Describe un patrón de URL sospechosa."""
    name: str
    regex: str

# Rules / patterns
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
    ProbeRule(name="env_files",                regex=r"^/(?:app|backend|core|api)/\.env(?:\..*)?$|^/\.env(?:\..*)?$"),
    ProbeRule(name="git_metadata",             regex=r"^/\.git(?:/config)?/?$"),
    ProbeRule(name="phpinfo",                  regex=r"^/phpinfo\.php$"),
    ProbeRule(name="phpunit_vendor",           regex=r"^/vendor/phpunit(?:/|$)"),
    ProbeRule(name="phpmyadmin",               regex=r"^/(?:phpmyadmin|pma|myadmin)(?:/|$)"),
    ProbeRule(name="storage_logs",             regex=r"^/storage/logs(?:/|$)"),
    ProbeRule(name="backup_files",             regex=r"\.(?:sql|zip|tar|gz|bak)$"),
]

_COMPILED = [(rule.name, re.compile(rule.regex, re.IGNORECASE)) for rule in PROBE_RULES]
logger = logging.getLogger("security")

SAFE_PATH_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
    "/accounts/",
    "/appointments/",
    "/services/",
    "/products/",
)

SAFE_PATH_PATTERNS = (
    re.compile(r"^/[a-z]{2}/admin/", re.IGNORECASE),
)

def path_looks_suspicious(path: str) -> bool:
    """Devuelve True si el path coincide con algún patrón sospechoso."""
    if path.startswith(SAFE_PATH_PREFIXES):
        return False

    for safe_pattern in SAFE_PATH_PATTERNS:
        if safe_pattern.search(path):
            return False

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
            logger.warning("Blocked suspicious probe path", extra={"path": request.path})
            return HttpResponseNotFound()
        return self.get_response(request)
