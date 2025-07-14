# core/whitenoise_headers.py
def add_custom_headers(headers, path, url):
    """
    Añade cabeceras extra a los ficheros estáticos servidos por WhiteNoise.
    """
    headers['X-Content-Type-Options'] = 'nosniff'
    # Si no estuviera ya, añade caché largo e immutable
    if 'Cache-Control' not in headers:
        headers['Cache-Control'] = 'public, max-age=31536000, immutable'
