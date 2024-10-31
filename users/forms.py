from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django_recaptcha.fields import ReCaptchaField

# Formulario de creación de usuario personalizado
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    phone = forms.CharField(max_length=15, required=True, label='Teléfono')
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

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
        if commit:
            user.save()
        phone = self.cleaned_data["phone"]
        UserProfile.objects.create(user=user, telefono=phone, email=user.email)
        return user

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
