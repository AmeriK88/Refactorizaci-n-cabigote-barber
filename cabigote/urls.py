from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.views.generic import TemplateView

from core.views import home

# 1️⃣  Service-worker en la raíz (sin prefijo /es/)
urlpatterns = [
    path(
        'sw.js',
        TemplateView.as_view(
            template_name='sw.js',
            content_type='application/javascript'
        ),
        name='sw.js'
    ),
    # Cambio de idioma
    path('i18n/', include('django.conf.urls.i18n')),
]

# 2️⃣  El resto de rutas traducibles
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('appointments/', include('appointments.urls')),
    path('products/', include('products.urls')),
    path('reviews/', include('reviews.urls')),
    path('services/', include('services.urls')),
    path('users/', include('users.urls')),
    path('reports/', include('reports.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
)

# 3️⃣  Media
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
