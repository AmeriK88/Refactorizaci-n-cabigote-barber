from django.urls import path
from .views import lanzar_recordatorios

urlpatterns = [
    path('lanzar-recordatorios/', lanzar_recordatorios, name='lanzar_recordatorios'),
]
