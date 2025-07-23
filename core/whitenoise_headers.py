import re
FINGERPRINT_RE = re.compile(r'\.[0-9a-f]{7,32}\.')

def add_custom_headers(headers, path, url):
    """WhiteNoise hook para cabeceras personalizadas."""
    headers['X-Content-Type-Options'] = 'nosniff'

    if FINGERPRINT_RE.search(path):
        # Assets con hash → cacheo agresivo
        headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    else:
        # Assets “normales” → 1 hora
        headers['Cache-Control'] = 'public, max-age=3600'
