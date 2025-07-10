from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.views import home
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve

urlpatterns = [
    # Necesario para cambiar idioma
    path('i18n/', include('django.conf.urls.i18n')),
]

# Rutas con i18n (sin incluir la ruta de media)
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

# Rutas para archivos media fuera de i18n_patterns
# Esta ruta sirve los archivos de media en producción (aunque no es ideal para alto tráfico)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Opcional: Si DEBUG es True, Django puede agregar esta ruta automáticamente
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
