from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.web.decorators import handle_exceptions
from users.forms import CustomUserCreationForm, CustomAuthenticationForm


from django.conf import settings

@handle_exceptions
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            password = form.cleaned_data.get("password1")
            authed_user = authenticate(request, username=user.username, password=password)

            if authed_user is None:
                auth_login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
            else:
                auth_login(request, authed_user)

            messages.success(
                request,
                f"¡Échale mojo! Bienvenido a Ca'Bigote, {user.username} ¡Cuenta operativa!",
            )
            return redirect("users:perfil_usuario")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/register.html", {"form": form})



@handle_exceptions
def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"¿¡Que pasó viejito!? ¡Bienvenido de nuevo, {user.username}!")
            return redirect(next_url or "users:perfil_usuario")
        messages.error(request, "¡Eres un tolete! Nombre de usuario o contraseña incorrectos.")
    else:
        form = CustomAuthenticationForm(request)

    return render(request, "users/login.html", {"form": form, "next": next_url})


@login_required
@handle_exceptions
def logout_view(request):
    username = request.user.username
    auth_logout(request)
    messages.success(request, f"¡Nos vemos, {username}, vuelve pronto puntalillo!")
    return redirect("home")
