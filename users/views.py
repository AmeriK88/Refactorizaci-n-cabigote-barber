from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, UserForm, CustomAuthenticationForm  
from core.decorators import handle_exceptions
from appointments.models import Cita 
from django.db import transaction

# Registro de usuario
@handle_exceptions
def register(request):
    if request.method == 'POST':
        # Crea un formulario de registro con los datos del usuario
        form = CustomUserCreationForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el nuevo usuario
            user = form.save()
            # Autentica para que el objeto user tenga el atributo `backend` cuando hay
            # múltiples backends configurados. Si por alguna razón authenticate falla,
            # asignamos el primer backend configurado como fallback.
            password = form.cleaned_data.get('password1')
            authed_user = authenticate(request, username=user.username, password=password)
            if authed_user is None:
                from django.conf import settings
                # set backend attribute so auth_login can proceed
                user.backend = settings.AUTHENTICATION_BACKENDS[0]
                auth_login(request, user)
            else:
                auth_login(request, authed_user)
            messages.success(request, f'¡¡Échale mojo! Bienvenido a Ca\'Bigote, {user.username}! Cuenta operativa.!')
            # Redirige al perfil del usuario
            return redirect('users:perfil_usuario')  
    else:
        # Si no es POST, muestra el formulario vacío
        form = CustomUserCreationForm() 
    return render(request, 'users/register.html', {'form': form})

# Inicio de sesión
@handle_exceptions
def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        # ¡Importante!: pasa request al form para que django-axes funcione
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'¿¡Que pasó viejito!? ¡Bienvenido de nuevo, {user.username}!')
            return redirect(next_url or 'users:perfil_usuario')
        else:
            messages.error(request, '¡Eres un tolete! Nombre de usuario o contraseña incorrectos.')
    else:
        # También en GET se pasa request
        form = CustomAuthenticationForm(request)

    return render(request, 'users/login.html', {'form': form, 'next': next_url})


# Cierre de sesión
@login_required
@handle_exceptions
def logout_view(request):
    # Obtiene el nombre de usuario
    username = request.user.username  
    # Cierra la sesión del usuario
    auth_logout(request)  
    messages.success(request, f'¡Nos vemos, {username}, vuelve pronto puntalillo!')  
    return redirect('home')  

# Perfil de usuario
@login_required
@handle_exceptions
def perfil_usuario(request):
    # Año actual (zona horaria de Django)
    current_year = timezone.localdate().year

    citas_activas = Cita.objects.filter(
        usuario=request.user,
        fecha__gte=timezone.now()
    ).select_related("servicio").order_by("fecha", "hora")

    # Solo citas del año actual
    citas_year = Cita.objects.filter(
        usuario=request.user,
        fecha__year=current_year
    ).select_related("servicio")

    total_citas_year = citas_year.count()
    total_gastado_year = citas_year.aggregate(total=Sum("servicio__precio"))["total"] or 0

    fav_service_data = (
        citas_year.values("servicio__nombre")
        .annotate(service_count=Count("servicio"))
        .order_by("-service_count")
        .first()
    )
    favorite_service_year = fav_service_data["servicio__nombre"] if fav_service_data else "N/A"

    context = {
        "year": current_year,
        "citas": citas_activas,
        "total_citas": total_citas_year,
        "total_gastado": total_gastado_year,
        "favorite_service": favorite_service_year,
    }
    return render(request, "users/perfil_usuario.html", context)


# Edición de perfil
@login_required
@handle_exceptions
def editar_perfil_usuario(request):
    # Obtiene o crea el perfil de usuario relacionado
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Crea formularios con los datos enviados por el usuario
        profile_form  = UserProfileForm(request.POST, instance=user_profile)
        user_form     = UserForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        # Verifica si los formularios son válidos
        if profile_form.is_valid() and user_form.is_valid() and password_form.is_valid():
            user_form.save()          # guarda cambios de User
            profile_form.save()       # guarda cambios de perfil
            password_form.save()      # cambia contraseña
            update_session_auth_hash(request, request.user)  # mantiene sesión
            messages.success(request, '!El que quiera lapas que se moje el culo¡. Perfil actualizado exitosamente.')
            return redirect('users:perfil_usuario')
        else:
            messages.error(request, '!Chacho¡ Tu o el servidor están en la parra. Prueba de nuevo.')
    else:
        # Si no es POST, muestra los formularios con los datos actuales
        profile_form  = UserProfileForm(instance=user_profile)
        user_form     = UserForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

    # ─── NUEVA LÍNEA ───
    has_google = request.user.socialaccount_set.filter(provider="google").exists()

    context = {
        'profile_form':  profile_form,
        'user_form':     user_form,
        'password_form': password_form,
        'username':      request.user.username,
        'current_email': request.user.email,
        'current_phone': user_profile.telefono,
        'has_google':    has_google,           # ← ya definido
    }

    return render(request, 'users/editar_perfil_usuario.html', context)


# Delete account
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        with transaction.atomic():
            # 1) Anonimizar perfil (opcional, pero recomendable)
            UserProfile.objects.filter(user=user).update(
                nombre     = '',
                apellido   = '',
                email      = '',
                telefono   = ''
            )
            # 2) Anonimizar / desactivar cuenta
            user.is_active = False
            user.email     = ''
            user.username  = f'deleted_{user.pk}'
            user.save(update_fields=['is_active', 'email', 'username'])
        # 3) Cerrar sesión y avisar
        auth_logout(request)
        messages.info(request, 'Tu cuenta ha sido desactivada. ¡Vuelve cuando quieras, puntal!')
        return redirect('home')

    # GET → página de confirmación
    return render(request, 'users/account_delete_confirm.html')

