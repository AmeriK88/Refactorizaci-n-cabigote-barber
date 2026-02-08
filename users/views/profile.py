from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.web.decorators import handle_exceptions

from users.forms import ProfileDataForm
from users.selectors.profiles import get_profile
from users.services.profiles import update_profile_data, deactivate_account

from appointments.selectors.user_dashboard import get_user_profile_dashboard


@login_required
@handle_exceptions
def perfil_usuario(request):
    context = get_user_profile_dashboard(user=request.user)
    return render(request, "users/perfil_usuario.html", context)



@login_required
@handle_exceptions
def editar_perfil_usuario(request):
    profile = get_profile(user=request.user)

    if request.method == "POST":
        form = ProfileDataForm(user=request.user, data=request.POST)
        if form.is_valid():
            update_profile_data(
                user=request.user,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                email=form.cleaned_data["email"],
                telefono=form.cleaned_data["telefono"],
            )
            messages.success(request, "!El que quiera lapas que se moje el culo¡. Perfil actualizado exitosamente.")
            return redirect("users:perfil_usuario")
        messages.error(request, "!Chacho¡ Tu o el servidor están en la parra. Prueba de nuevo.")
    else:
        form = ProfileDataForm(
            user=request.user,
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "telefono": profile.telefono,
            },
        )

    has_google = request.user.socialaccount_set.filter(provider="google").exists()

    context = {
        "form": form,
        "username": request.user.username,
        "current_email": request.user.email,
        "current_phone": profile.telefono,
        "has_google": has_google,
    }
    return render(request, "users/editar_perfil_usuario.html", context)




@login_required
@handle_exceptions
def delete_account(request):
    if request.method == "POST":
        deactivate_account(user=request.user)
        auth_logout(request)
        messages.info(request, "Tu cuenta ha sido desactivada. ¡Vuelve cuando quieras, puntal!")
        return redirect("home")

    return render(request, "users/account_delete_confirm.html")

