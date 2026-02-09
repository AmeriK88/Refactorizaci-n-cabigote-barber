import re

FINGERPRINT_RE = re.compile(r'\.[0-9a-f]{7,32}\.')

def add_custom_headers(headers, path, url):
    """WhiteNoise hook para cabeceras personalizadas."""
    headers["X-Content-Type-Options"] = "nosniff"

    # ✅ Service worker: siempre revalidar (si no, no llegan updates)
    if url.endswith("/sw.js") or path.endswith("sw.js"):
        headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        headers["Pragma"] = "no-cache"
        headers["Expires"] = "0"
        return

    # ✅ Manifest: mejor revalidar también
    if url.endswith("/manifest.json") or path.endswith("manifest.json"):
        headers["Cache-Control"] = "no-cache"
        return

    # Assets con hash → cacheo agresivo
    if FINGERPRINT_RE.search(path):
        headers["Cache-Control"] = "public, max-age=31536000, immutable"
    else:
        # Assets “normales” → 1 hora
        headers["Cache-Control"] = "public, max-age=3600"
