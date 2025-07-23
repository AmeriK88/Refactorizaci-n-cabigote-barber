from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('reservar/<int:servicio_id>/', views.reservar_cita, name='reservar_cita'),
    path('reservar/', views.reservar_cita, name='reservar_cita'),
    path('ver/', views.ver_citas, name='ver_citas'),
    path('editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('eliminar/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
]
