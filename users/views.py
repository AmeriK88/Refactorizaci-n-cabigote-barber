from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, UserForm, CustomAuthenticationForm  
from core.decorators import handle_exceptions
from appointments.models import Cita 

# Registro de usuario
@handle_exceptions
def register(request):
    if request.method == 'POST':
        # Crea un formulario de registro con los datos del usuario
        form = CustomUserCreationForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el nuevo usuario y lo autentica
            user = form.save()
            auth_login(request, user)
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
    if request.method == 'POST':
        # Crea un formulario de autenticación con los datos de la solicitud
        form = CustomAuthenticationForm(data=request.POST)  
        # Verifica si el formulario es válido
        if form.is_valid():
            # Obtiene el usuario autenticado & inicia sesión
            user = form.get_user()  
            auth_login(request, user)  
            messages.success(request, f'¿¡Que pasó viejito!?¡Bienvenido de nuevo, {user.username}!') 
            return redirect('users:perfil_usuario')  
        else:
            messages.error(request, '¡Eres un tolete! Nombre de usuario o contraseña incorrectos.')  
    else:
        # Si no es POST, muestra el formulario vacío
        form = CustomAuthenticationForm()  
    return render(request, 'users/login.html', {'form': form}) 

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
    # Obtener citas activas ordenadas por fecha (incluso las horas)
    citas_activas = Cita.objects.filter(
        usuario=request.user, 
        fecha__gte=timezone.now()
    ).order_by('fecha', 'hora')
    return render(request, 'users/perfil_usuario.html', {'citas': citas_activas})


# Edición de perfil
@login_required
@handle_exceptions
def editar_perfil_usuario(request):
    # Obtiene o crea el perfil de usuario relacionado
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Crea formularios con los datos enviados por el usuario
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        user_form = UserForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        
        # Verifica si los formularios son válidos
        if profile_form.is_valid() and user_form.is_valid() and password_form.is_valid():
            user_form.save()  
            # Guarda los cambios del perfil & cambia contraseña
            profile_form.save()  
            password_form.save() 
            
            # Mantiene la sesión activa después de cambiar la contraseña
            update_session_auth_hash(request, request.user)  
            messages.success(request, '!El que quiera lapas que se moje el culo¡. Perfil actualizado exitosamente.') 
            return redirect('users:perfil_usuario')  
        else:
            messages.error(request, '!Chacho¡ Tu o el servidor están en la parra. Prueba de nuevo.') 
    else:
        # Si no es POST, muestra los formularios con los datos actuales
        profile_form = UserProfileForm(instance=user_profile)
        user_form = UserForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'password_form': password_form,
        'username': request.user.username,
        'current_email': request.user.email,
        'current_phone': user_profile.telefono
    }
    
    return render(request, 'users/editar_perfil_usuario.html', context)  
