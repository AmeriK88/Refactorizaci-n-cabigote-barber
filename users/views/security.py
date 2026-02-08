from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.web.decorators import handle_exceptions

from users.forms import PasswordChangeFormSafe


@login_required
@handle_exceptions
def password_change_view(request):
    if request.method == "POST":
        form = PasswordChangeFormSafe(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "¡Puntal! Contraseña actualizada correctamente.")
            return redirect("users:editar_perfil_usuario")
        messages.error(request, "Revisa los campos: no se pudo cambiar la contraseña.")
    else:
        form = PasswordChangeFormSafe(user=request.user)

    return render(request, "users/security_password_change.html", {"form": form})

