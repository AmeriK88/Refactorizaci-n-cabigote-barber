# reviews/urls.py
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ver_resenas, name='ver_resenas'),
]
