"""Insignias de estado reutilizables para columnas de list_display.

Los estilos viven en adminDashboard.css (.cb-badge). Todo el HTML se genera con
format_html, de modo que ningún dato de usuario llega sin escapar.
"""

from django.utils.html import format_html
from django.utils.translation import gettext


def status_badge(flag, glyph_yes="✓", glyph_no="✕"):
    """Sí/No con texto visible; el glifo es decorativo y el color no es el único indicador."""
    flag = bool(flag)
    return format_html(
        '<span class="cb-badge cb-badge--{}"><span class="cb-badge__icon" aria-hidden="true">{}</span>{}</span>',
        "yes" if flag else "no",
        glyph_yes if flag else glyph_no,
        gettext("Yes") if flag else gettext("No"),
    )


def rating_badge(value, maximum=5):
    """Puntuación como «n/5» legible, con estrellas decorativas."""
    value = max(0, min(int(value or 0), maximum))
    return format_html(
        '<span class="cb-badge cb-badge--rating" title="{value}/{maximum}">'
        '<span class="cb-badge__icon" aria-hidden="true">{stars}</span>{value}/{maximum}</span>',
        value=value,
        maximum=maximum,
        stars="★" * value + "☆" * (maximum - value),
    )


def neutral_badge(text):
    return format_html('<span class="cb-badge cb-badge--neutral">{}</span>', text)
