# media/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('imagenes/', views.ver_imagenes, name='ver_imagenes'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
]
