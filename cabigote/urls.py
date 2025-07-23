from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from core.views import home
from django.utils import timezone
from appointments.models import Cita
from services.models import Servicio
from decimal import Decimal
from datetime import datetime, time, timedelta
from django.contrib.auth import get_user_model

# --- VISTA QUE ENVUELVE EL ÍNDICE DEL ADMIN ---
def admin_dashboard(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return admin.site.login(request)

    # 2) CALCULATE TODAY'S DATE RANGE
    local_tz = timezone.get_current_timezone()
    today = timezone.localdate()
    start_of_day = timezone.make_aware(datetime.combine(today, time.min), local_tz)
    end_of_day   = start_of_day + timedelta(days=1)

    # 3) FILTER RANGE
    citas_qs = (
        Cita.objects
            .filter(fecha__gte=start_of_day, fecha__lt=end_of_day)
            .select_related("producto", "servicio")
    )

    # 4) METRICS
    citas_hoy = citas_qs.count()
    ingresos_hoy = Decimal("0")
    for c in citas_qs:
        if c.servicio:
            ingresos_hoy += c.servicio.precio or 0
        if c.producto and hasattr(c.producto, "precio"):
            ingresos_hoy += c.producto.precio or 0

    # 5) TOTAL USERS
    User = get_user_model()
    usuarios_total = User.objects.count() 

    
    extra_context = {
        "citas_hoy":      citas_hoy,
        "ingresos_hoy":   ingresos_hoy,
        "servicios_total": Servicio.objects.count(),
        "usuarios_total":   usuarios_total,
    }
    # 6) CALL THE ADMIN INDEX VIEW
    admin_index = admin.site.admin_view(admin.site.index)
    return admin_index(request, extra_context=extra_context)

# ──────────────────────────────────────────────────────────
# Rutas sin prefijo de idioma
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
# Rutas traducibles
# ──────────────────────────────────────────────────────────
urlpatterns += i18n_patterns(
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
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
)

# Media y debug 
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
