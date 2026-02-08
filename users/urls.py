from django.urls import path

from .views.auth import login_view, logout_view, register
from .views.profile import perfil_usuario, editar_perfil_usuario, delete_account
from .views.security import password_change_view
from .views.connections import connections_view

app_name = "users"

urlpatterns = [
    # Auth
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register, name="register"),

    # Perfil
    path("perfil/", perfil_usuario, name="perfil_usuario"),
    path("perfil/editar/", editar_perfil_usuario, name="editar_perfil_usuario"),
    path("perfil/eliminar/", delete_account, name="delete_account"),

    # Seguridad
    path("perfil/seguridad/password/", password_change_view, name="password_change"),

    # Conexiones (Google)
    path("perfil/conexiones/", connections_view, name="connections"),
]
