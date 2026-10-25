from django.contrib import admin
from django.contrib.auth.views import PasswordResetView
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from core.views import home
from appointments.models import Cita
from appointments.services.dashboard_stats import (
    dashboard_appointment_summary,
    upcoming_appointments,
)
from services.models import Servicio
from reports.models import ReporteMensual
from django.contrib.auth import get_user_model
from core.views import home, custom_404_view

UPCOMING_LIMIT = 5


def _can_view(request, model):
    """Mismo criterio que el ModelAdmin: permiso de consulta o de modificación."""
    model_admin = admin.site._registry.get(model)
    return bool(model_admin and model_admin.has_view_permission(request))


# --- VIEW THAT WRAPS THE ADMIN INDEX ---
def admin_dashboard(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return admin.site.login(request)

    User = get_user_model()
    can_citas = _can_view(request, Cita)
    can_servicios = _can_view(request, Servicio)
    can_usuarios = _can_view(request, User)
    can_reportes = _can_view(request, ReporteMensual)

    # Los indicadores no autorizados no se consultan y llegan como None.
    citas_hoy = valor_estimado_hoy = servicios_total = usuarios_total = None
    citas_sin_ver = None
    proximas_citas = []

    if can_citas:
        summary = dashboard_appointment_summary()
        citas_hoy = summary["today"]
        valor_estimado_hoy = summary["estimated_value"]
        citas_sin_ver = summary["pending_review"]
        proximas_citas = upcoming_appointments(limit=UPCOMING_LIMIT)

    if can_servicios:
        servicios_total = Servicio.objects.count()
    if can_usuarios:
        usuarios_total = User.objects.count()

    extra_context = {
        "citas_hoy":      citas_hoy,
        "valor_estimado_hoy": valor_estimado_hoy,
        "servicios_total": servicios_total,
        "usuarios_total":   usuarios_total,
        "citas_sin_ver": citas_sin_ver,
        "proximas_citas": proximas_citas,
        "can_view_citas": can_citas,
        "can_view_usuarios": can_usuarios,
        "can_view_reportes": can_reportes,
        "show_kpis": can_citas or can_servicios or can_usuarios,
        "show_quick_actions": can_citas or can_usuarios or can_reportes,
    }
    # 6) CALL THE ADMIN INDEX VIEW
    admin_index = admin.site.admin_view(admin.site.index)
    return admin_index(request, extra_context=extra_context)

# ──────────────────────────────────────────────────────────
# Routes without language prefix
# ──────────────────────────────────────────────────────────
urlpatterns = [
    # ─── SW.js ─────────────────────────────────────────────
    path(
        "sw.js",
        never_cache(
            TemplateView.as_view(
                template_name="sw.js",
                content_type="application/javascript"
            )
        ),
        name="sw.js",
    ),
    path(
        "offline.html",
        TemplateView.as_view(template_name="offline.html"),
        name="offline",
    ),

    # ←─── LANG: vista set_language
    path("i18n/", include("django.conf.urls.i18n")),
]

# ──────────────────────────────────────────────────────────
# Routes with language prefix (i18n_patterns)
# ──────────────────────────────────────────────────────────
urlpatterns += i18n_patterns(
    path("offline.html", TemplateView.as_view(template_name="offline.html"), name="offline_i18n"),

    path("admin/", admin_dashboard, name="admin-dashboard"),    
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("appointments/", include("appointments.urls")),
    path("products/", include("products.urls")),
    path("reviews/", include("reviews.urls")),
    path("services/", include("services.urls")),
    path("users/", include("users.urls")),
    path("reports/", include("reports.urls")),
    path("accounts/", include("allauth.urls")),
    path(
        "accounts/password_reset/",
        PasswordResetView.as_view(
            email_template_name="registration/password_reset_email.txt",
            html_email_template_name="registration/password_reset_email_html.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = custom_404_view