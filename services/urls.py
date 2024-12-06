# services/urls.py
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ver_servicios, name='ver_servicios'),
]
