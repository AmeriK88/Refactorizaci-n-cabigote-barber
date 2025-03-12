from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Necesario para cambiar idioma
    path('i18n/', include('django.conf.urls.i18n')),  
]

# Envolver todas las rutas en i18n_patterns
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('appointments/', include('appointments.urls')), 
    path('products/', include('products.urls')),                
    path('reviews/', include('reviews.urls')),            
    path('services/', include('services.urls')),         
    path('users/', include('users.urls')),  
    path('reports/', include('reports.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
)

# **Rutas para archivos media fuera de i18n_patterns**
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
