from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django_recaptcha.fields import ReCaptchaField
from django.conf import settings

# Formulario de creación de usuario personalizado
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    phone = forms.CharField(max_length=15, required=True, label='Teléfono')
    nombre = forms.CharField(max_length=30, required=True, label='Nombre')
    apellido = forms.CharField(max_length=30, required=True, label='Apellido')
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ("username", "email", "phone", "nombre", "apellido", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["nombre"] 
        user.last_name = self.cleaned_data["apellido"]  
        if commit:
            user.save()
        # Guardar datos adicionales en el perfil
        phone = self.cleaned_data["phone"]
        nombre = self.cleaned_data["nombre"]
        apellido = self.cleaned_data["apellido"]
        UserProfile.objects.create(
            user=user,
            telefono=phone,
            email=user.email,
            nombre=nombre,
            apellido=apellido
        )
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')

        # Verificar si el nombre de usuario está en la lista negra
        if username == 'admin' and not self.instance.is_superuser:
            raise forms.ValidationError(f"El nombre de usuario '{username}' está prohibido.")
    
        if username in settings.BLACKLISTED_USERNAMES:
            raise forms.ValidationError(f"El nombre de usuario '{username}' está prohibido.")

        return username

# Formulario de autenticación personalizado
class CustomAuthenticationForm(AuthenticationForm):
    captcha = ReCaptchaField()

# Formulario de perfil de usuario
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'telefono']
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'telefono': forms.TextInput(attrs={'autocomplete': 'tel'}),
        }

# Formulario de actualización de email
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'id': 'user-email'}),
        }
