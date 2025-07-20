# users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil_usuario, name='editar_perfil_usuario'),
    path('perfil/eliminar/', views.delete_account, name='delete_account'),
]
