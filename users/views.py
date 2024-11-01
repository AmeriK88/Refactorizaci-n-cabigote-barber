from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, UserForm
from core.decorators import handle_exceptions
from appointments.models import Cita 

# Registro de usuario
@handle_exceptions
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'¡¡Échale mojo! Bienvenido a Ca\'Bigote, {user.username}! Cuenta operativa.!')
            return redirect('users:perfil_usuario') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})  

# Inicio de sesión
@handle_exceptions
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'¿¡Que pasó viejito!?¡Bienvenido de nuevo, {user.username}!') 
            return redirect('users:perfil_usuario')  
        else:
            messages.error(request, '¡Eres un tolete! Nombre de usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# Cierre de sesión
@login_required
@handle_exceptions
def logout_view(request):
    username = request.user.username
    auth_logout(request)
    messages.success(request, f'¡Nos vemos, {username}, vuelve pronto puntalillo!')
    return redirect('home')  

# Perfil de usuario
@login_required
@handle_exceptions
def perfil_usuario(request):
    citas_activas = Cita.objects.filter(usuario=request.user, fecha__gte=timezone.now()).order_by('fecha')
    return render(request, 'users/perfil_usuario.html', {'citas': citas_activas})  

# Edición de perfil
@login_required
@handle_exceptions
def editar_perfil_usuario(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        user_form = UserForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if profile_form.is_valid() and user_form.is_valid() and password_form.is_valid():
            user_form.save()
            profile_form.save()
            password_form.save()
            
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('users:perfil_usuario')  
        else:
            messages.error(request, 'Hubo un problema al actualizar tu perfil.')
    else:
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
