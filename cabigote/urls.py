# cabigote/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('appointments/', include('appointments.urls')), 
    path('media/', include('media.urls')),                
    path('reviews/', include('reviews.urls')),            
    path('services/', include('services.urls')),         
    path('users/', include('users.urls')),  
    path('accounts/', include('django.contrib.auth.urls')),          
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
    # Agrega aquí otras URLs que necesites traducir
)
